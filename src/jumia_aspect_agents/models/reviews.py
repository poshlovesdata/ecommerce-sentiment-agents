"""Data contracts for raw Jumia review collection."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ProductSummary(BaseModel):
    """Minimal product metadata discovered from a category page."""

    product_name: str
    product_url: str
    sku: str | None = None
    listing_rating: float | None = None
    listing_review_count: int | None = None


class RawReview(BaseModel):
    """A single unprocessed review as collected from Jumia."""

    product_name: str
    product_url: str
    sku: str | None = None
    review_title: str | None = None
    review_body: str | None = None
    star_rating: int | None = Field(default=None, ge=1, le=5)
    review_date: str | None = None
    reviewer_name: str | None = None
    verified_purchase: bool = False
    source_url: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScrapeResult(BaseModel):
    """Summary returned by a scraping run."""

    category_url: str
    products_seen: int
    product_pages_visited: int
    reviews_collected: int
    output_csv: str | None = None
    output_json: str | None = None
