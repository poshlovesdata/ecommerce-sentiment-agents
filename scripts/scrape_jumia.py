"""CLI entrypoint for scraping Jumia Nigeria reviews."""

import argparse
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jumia_aspect_agents.data_collection.scraper import JumiaReviewScraper, ScraperConfig  # noqa: E402
from jumia_aspect_agents.utils.logging import configure_logging  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Jumia Nigeria mobile accessory reviews.")
    parser.add_argument(
        "--category-url",
        default="https://www.jumia.com.ng/mobile-accessories/",
        help="Jumia category URL to scrape.",
    )
    parser.add_argument("--max-pages", type=int, default=1, help="Category pages to inspect.")
    parser.add_argument("--max-products", type=int, default=10, help="Maximum products to visit.")
    parser.add_argument(
        "--max-reviews-per-product",
        type=int,
        default=20,
        help="Maximum reviews to collect per product.",
    )
    parser.add_argument(
        "--max-review-pages-per-product",
        type=int,
        default=3,
        help="Maximum paginated review pages to fetch for each product.",
    )
    parser.add_argument(
        "--min-listing-review-count",
        type=int,
        default=1,
        help="Only visit products whose listing card shows at least this many reviews.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory where raw CSV/JSON files will be written.",
    )
    parser.add_argument("--log-level", default="INFO", help="Loguru log level.")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional structured log file path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(level=args.log_level, log_file=args.log_file)

    config = ScraperConfig(
        category_url=args.category_url,
        max_pages=args.max_pages,
        max_products=args.max_products,
        max_reviews_per_product=args.max_reviews_per_product,
        max_review_pages_per_product=args.max_review_pages_per_product,
        min_listing_review_count=args.min_listing_review_count,
        output_dir=args.output_dir,
    )
    result = JumiaReviewScraper(config).scrape()
    logger.success("Collected {} reviews", result.reviews_collected)
    logger.success("CSV: {}", result.output_csv)
    logger.success("JSON: {}", result.output_json)


if __name__ == "__main__":
    main()
