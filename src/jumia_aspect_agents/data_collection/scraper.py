"""Responsible Jumia Nigeria review scraper."""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from jumia_aspect_agents.config import settings
from jumia_aspect_agents.models.reviews import ProductSummary, RawReview, ScrapeResult
from jumia_aspect_agents.utils.io import write_records_csv_json


USER_AGENTS = [
    "PoshLovesDataResearchBot/0.1 (+https://poshlovesdata.dev; COSC878 research)",
    "JumiaAspectResearchBot/0.1 (+https://poshlovesdata.dev; educational research)",
    "ConsumerAnalyticsResearchBot/0.1 (+https://poshlovesdata.dev; contact via site)",
]


@dataclass(frozen=True)
class ScraperConfig:
    """Runtime controls for the scraper."""

    category_url: str = str(settings.jumia_category_url)
    base_url: str = str(settings.jumia_base_url)
    max_pages: int = 1
    max_products: int = 10
    max_reviews_per_product: int = 20
    max_review_pages_per_product: int = 3
    min_listing_review_count: int = 1
    min_delay_seconds: int = settings.scraper_min_delay_seconds
    max_delay_seconds: int = settings.scraper_max_delay_seconds
    timeout_seconds: int = settings.scraper_timeout_seconds
    output_dir: Path = settings.raw_data_dir


class JumiaReviewScraper:
    """Collect raw product reviews from Jumia category and product pages."""

    def __init__(self, config: ScraperConfig | None = None) -> None:
        self.config = config or ScraperConfig()
        self.session = requests.Session()

    def scrape(self) -> ScrapeResult:
        """Collect reviews and save them as raw CSV and JSON files."""

        logger.info("Starting Jumia scrape from {}", self.config.category_url)
        products = self.discover_products()
        reviews: list[RawReview] = []

        for index, product in enumerate(products, start=1):
            logger.info(
                "Collecting reviews for product {}/{}: {}",
                index,
                len(products),
                product.product_name,
            )
            self._polite_delay()
            reviews.extend(self.collect_product_reviews(product))

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_csv = self.config.output_dir / f"jumia_reviews_raw_{timestamp}.csv"
        output_json = self.config.output_dir / f"jumia_reviews_raw_{timestamp}.json"
        write_records_csv_json(reviews, csv_path=output_csv, json_path=output_json)

        result = ScrapeResult(
            category_url=self.config.category_url,
            products_seen=len(products),
            product_pages_visited=len(products),
            reviews_collected=len(reviews),
            output_csv=str(output_csv),
            output_json=str(output_json),
        )
        logger.info("Scrape completed: {}", result.model_dump())
        return result

    def discover_products(self) -> list[ProductSummary]:
        """Read category pages and return product URLs to visit."""

        products_by_url: dict[str, ProductSummary] = {}

        for page_number in range(1, self.config.max_pages + 1):
            page_url = self._category_page_url(page_number)
            logger.info("Fetching category page {}", page_url)
            html = self.fetch(page_url)
            page_products = self.parse_category_products(html)

            logger.info("Discovered {} product links on page {}", len(page_products), page_number)
            for product in page_products:
                products_by_url.setdefault(product.product_url, product)

            self._polite_delay()

        products = [
            product
            for product in products_by_url.values()
            if (product.listing_review_count or 0) >= self.config.min_listing_review_count
        ]
        return sorted(
            products,
            key=lambda product: product.listing_review_count or 0,
            reverse=True,
        )[: self.config.max_products]

    def collect_product_reviews(self, product: ProductSummary) -> list[RawReview]:
        """Collect reviews from the product page and, when available, its reviews page."""

        html = self.fetch(product.product_url)
        soup = BeautifulSoup(html, "lxml")
        product = self._hydrate_product_from_page(product, soup)

        review_source_url = self._find_reviews_page_url(soup, product)
        if review_source_url and product.sku is None:
            product = product.model_copy(update={"sku": self._extract_sku_from_reviews_url(review_source_url)})
        if review_source_url:
            reviews = self.collect_paginated_reviews(product, review_source_url)
            if not reviews:
                logger.warning("Reviews page had no parsed reviews; falling back to product page")
                reviews = self.parse_reviews(html, product, source_url=product.product_url)
        else:
            reviews = self.parse_reviews(html, product, source_url=product.product_url)

        return reviews[: self.config.max_reviews_per_product]

    def collect_paginated_reviews(
        self,
        product: ProductSummary,
        first_reviews_url: str,
    ) -> list[RawReview]:
        """Collect reviews across a product's paginated review pages."""

        reviews: list[RawReview] = []
        seen_keys: set[tuple[str | None, str | None, str | None, int | None]] = set()
        current_url: str | None = first_reviews_url

        for page_number in range(1, self.config.max_review_pages_per_product + 1):
            if current_url is None or len(reviews) >= self.config.max_reviews_per_product:
                break

            logger.info("Fetching review page {} for SKU {}", page_number, product.sku)
            self._polite_delay()
            html = self.fetch(current_url)
            page_reviews = self.parse_reviews(html, product, source_url=current_url)

            new_reviews = []
            for review in page_reviews:
                key = (
                    review.review_date,
                    review.reviewer_name,
                    review.review_title,
                    review.star_rating,
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                new_reviews.append(review)

            if not new_reviews:
                logger.info("No new reviews found on review page {}; stopping pagination", page_number)
                break

            reviews.extend(new_reviews)
            if len(reviews) >= self.config.max_reviews_per_product:
                break

            current_url = self._find_next_reviews_page_url(html, current_url, page_number + 1)

        return reviews[: self.config.max_reviews_per_product]

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(settings.scraper_max_retries),
        reraise=True,
    )
    def fetch(self, url: str) -> str:
        """Fetch a page with browser-like headers and retry transient failures."""

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        response = self.session.get(url, headers=headers, timeout=self.config.timeout_seconds)
        response.raise_for_status()
        return response.text

    def parse_category_products(self, html: str) -> list[ProductSummary]:
        """Extract product links from a category listing page."""

        soup = BeautifulSoup(html, "lxml")
        products: list[ProductSummary] = []

        candidate_links = soup.select("article.prd a.core[href], a.core[href]")
        if not candidate_links:
            candidate_links = [
                link
                for link in soup.select("a[href]")
                if self._looks_like_product_url(link.get("href", ""))
            ]

        for link in candidate_links:
            href = link.get("href")
            if not href or not self._looks_like_product_url(href):
                continue

            product_url = urljoin(self.config.base_url, href)
            product_name = self._extract_product_name_from_card(link)
            if not product_name:
                continue

            card_text = link.get_text(" ", strip=True)
            products.append(
                ProductSummary(
                    product_name=product_name,
                    product_url=product_url,
                    sku=self._extract_sku_from_url(product_url),
                    listing_rating=self._extract_float(card_text),
                    listing_review_count=self._extract_review_count(card_text),
                )
            )

        return self._dedupe_products(products)

    def parse_reviews(
        self,
        html: str,
        product: ProductSummary,
        *,
        source_url: str,
    ) -> list[RawReview]:
        """Extract review records from a product or reviews page."""

        soup = BeautifulSoup(html, "lxml")
        review_nodes = self._find_review_nodes(soup)
        reviews = [
            review
            for node in review_nodes
            if (review := self._parse_review_node(node, product, source_url=source_url)) is not None
        ]

        if reviews:
            return reviews

        return self._parse_reviews_from_text(soup.get_text("\n", strip=True), product, source_url)

    def _parse_review_node(
        self,
        node: Tag,
        product: ProductSummary,
        *,
        source_url: str,
    ) -> RawReview | None:
        text = node.get_text("\n", strip=True)
        rating = self._extract_rating(text)
        if rating is None:
            return None

        title = self._first_text(node.select("h3, .ttl, [class*='title']"))
        body = self._first_text(node.select("p, .cmt, [class*='comment']"))
        review_date, reviewer_name = self._extract_date_and_reviewer(text)

        if not body:
            body = self._body_from_review_text(text, title)

        return RawReview(
            product_name=product.product_name,
            product_url=product.product_url,
            sku=product.sku,
            review_title=title,
            review_body=body,
            star_rating=rating,
            review_date=review_date,
            reviewer_name=reviewer_name,
            verified_purchase="Verified Purchase" in text,
            source_url=source_url,
        )

    def _parse_reviews_from_text(
        self,
        text: str,
        product: ProductSummary,
        source_url: str,
    ) -> list[RawReview]:
        """Fallback parser for simplified rendered text."""

        marker = "Comments from Verified Purchases"
        if marker in text:
            text = text.split(marker, maxsplit=1)[1]

        pattern = re.compile(
            r"(?P<rating>[1-5])\s+out of 5\s+"
            r"(?P<title>.+?)\s+"
            r"(?P<body>.+?)\s+"
            r"(?P<date>\d{2}-\d{2}-\d{4})\s+by\s+(?P<reviewer>.+?)\s+"
            r"Verified Purchase",
            flags=re.DOTALL,
        )

        reviews: list[RawReview] = []
        for match in pattern.finditer(text):
            reviews.append(
                RawReview(
                    product_name=product.product_name,
                    product_url=product.product_url,
                    sku=product.sku,
                    review_title=self._clean_text(match.group("title")),
                    review_body=self._clean_text(match.group("body")),
                    star_rating=int(match.group("rating")),
                    review_date=match.group("date"),
                    reviewer_name=self._clean_text(match.group("reviewer")),
                    verified_purchase=True,
                    source_url=source_url,
                )
            )
        return reviews

    def _hydrate_product_from_page(
        self,
        product: ProductSummary,
        soup: BeautifulSoup,
    ) -> ProductSummary:
        name = self._first_text(soup.select("h1")) or product.product_name
        sku = product.sku or self._extract_sku_from_text(soup.get_text(" ", strip=True))
        return ProductSummary(
            product_name=name,
            product_url=product.product_url,
            sku=sku,
            listing_rating=product.listing_rating,
            listing_review_count=product.listing_review_count,
        )

    def _find_reviews_page_url(self, soup: BeautifulSoup, product: ProductSummary) -> str | None:
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            if "/catalog/productratingsreviews/sku/" in href:
                return urljoin(self.config.base_url, href)

        if product.sku:
            return urljoin(
                self.config.base_url,
                f"/catalog/productratingsreviews/sku/{product.sku}/",
            )
        return None

    def _find_next_reviews_page_url(
        self,
        html: str,
        current_url: str,
        next_page_number: int,
    ) -> str | None:
        soup = BeautifulSoup(html, "lxml")

        for link in soup.select("a[href]"):
            text = self._clean_text(link.get_text(" ", strip=True)) or ""
            rel = " ".join(link.get("rel", [])) if isinstance(link.get("rel"), list) else ""
            href = link.get("href", "")
            if text.lower() in {"next", ">", "›"} or "next" in rel.lower():
                return urljoin(self.config.base_url, href)

        return self._with_page_param(current_url, next_page_number)

    def _find_review_nodes(self, soup: BeautifulSoup) -> list[Tag]:
        selectors = [
            "article.-pvs",
            "article[class*='-pvs']",
            "div[class*='review'] article",
        ]

        nodes: list[Tag] = []
        for selector in selectors:
            nodes.extend(soup.select(selector))

        unique_nodes: list[Tag] = []
        seen: set[str] = set()
        for node in nodes:
            text = node.get_text(" ", strip=True)
            if text and text not in seen and "out of 5" in text:
                unique_nodes.append(node)
                seen.add(text)
        return unique_nodes

    def _category_page_url(self, page_number: int) -> str:
        if page_number <= 1:
            return self.config.category_url

        return self._with_page_param(self.config.category_url, page_number)

    def _with_page_param(self, url: str, page_number: int) -> str:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["page"] = str(page_number)
        return urlunparse(parsed._replace(query=urlencode(query)))

    def _polite_delay(self) -> None:
        delay = random.uniform(
            self.config.min_delay_seconds,
            self.config.max_delay_seconds,
        )
        logger.debug("Sleeping for {:.2f}s", delay)
        time.sleep(delay)

    def _looks_like_product_url(self, href: str) -> bool:
        parsed_path = urlparse(urljoin(self.config.base_url, href)).path
        return parsed_path.endswith(".html") and "catalog" not in parsed_path

    def _extract_product_name_from_card(self, link: Tag) -> str | None:
        for selector in ["h3.name", ".name", "h3", "[class*='name']"]:
            node = link.select_one(selector)
            if node:
                return self._clean_text(node.get_text(" ", strip=True))

        text = self._clean_text(link.get_text(" ", strip=True))
        if not text:
            return None
        return re.split(r"\s+\u20a6\s+|\s+\d(?:\.\d)?\s+out of 5", text, maxsplit=1)[0]

    def _extract_sku_from_url(self, url: str) -> str | None:
        match = re.search(r"-([A-Z0-9]{8,})\.html", url)
        return match.group(1) if match else None

    def _extract_sku_from_text(self, text: str) -> str | None:
        match = re.search(r"SKU:\s*([A-Z0-9]+)", text)
        return match.group(1) if match else None

    def _extract_sku_from_reviews_url(self, url: str) -> str | None:
        match = re.search(r"/sku/([A-Z0-9]+)/?", url)
        return match.group(1) if match else None

    def _extract_rating(self, text: str) -> int | None:
        match = re.search(r"\b([1-5])\s+out of 5\b", text)
        return int(match.group(1)) if match else None

    def _extract_float(self, text: str) -> float | None:
        match = re.search(r"\b([1-5](?:\.\d+)?)\s+out of 5\b", text)
        return float(match.group(1)) if match else None

    def _extract_review_count(self, text: str) -> int | None:
        match = re.search(r"\(([\d,]+)\)", text)
        return int(match.group(1).replace(",", "")) if match else None

    def _extract_date_and_reviewer(self, text: str) -> tuple[str | None, str | None]:
        match = re.search(r"(\d{2}-\d{2}-\d{4})\s+by\s+(.+?)(?:\s+Verified Purchase|$)", text)
        if not match:
            return None, None
        return match.group(1), self._clean_text(match.group(2))

    def _body_from_review_text(self, text: str, title: str | None) -> str | None:
        lines = [self._clean_text(line) for line in text.splitlines() if self._clean_text(line)]
        content = [
            line
            for line in lines
            if line != "Verified Purchase"
            and "out of 5" not in line
            and not re.search(r"\d{2}-\d{2}-\d{4}\s+by", line)
            and line != title
        ]
        return content[0] if content else None

    def _first_text(self, nodes: Iterable[Tag]) -> str | None:
        for node in nodes:
            text = self._clean_text(node.get_text(" ", strip=True))
            if text:
                return text
        return None

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        return re.sub(r"\s+", " ", value).strip()

    def _dedupe_products(self, products: list[ProductSummary]) -> list[ProductSummary]:
        deduped: dict[str, ProductSummary] = {}
        for product in products:
            deduped.setdefault(product.product_url, product)
        return list(deduped.values())
