"""Smoke test for the Streamlit dashboard."""

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest


def test_dashboard_renders_without_exceptions() -> None:
    write_processed_fixture()
    app = AppTest.from_file("app/streamlit_app.py")

    app.run(timeout=30)

    assert not app.exception
    assert len(app.title) == 1
    assert len(app.metric) == 5
    assert len(app.dataframe) == 1


def write_processed_fixture() -> None:
    output = Path("data/processed/jumia_reviews_processed_latest.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "review_id": "review-1",
                "product_name": "Ace Elec Power Bank",
                "product_url": "https://www.jumia.com.ng/product.html",
                "sku": "AC431EA7LKZHVNAFAMZ",
                "review_title": "Good product",
                "review_text": "The battery lasts long and delivery was fast.",
                "star_rating": 5,
                "review_date": "09-06-2026",
                "reviewer_name": "Ada",
                "verified_purchase": True,
                "source_url": "https://www.jumia.com.ng/reviews",
                "scraped_at": "2026-06-10T08:00:00+00:00",
                "cleaned_text": "The battery lasts long and delivery was fast.",
                "product_category": "Power Bank",
                "aspect": "Battery life",
                "aspect_category": "Battery life",
                "aspect_evidence": "battery lasts long",
                "vader_compound": 0.72,
                "vader_label": "positive",
                "contextual_sentiment": "positive",
                "contextual_sentiment_score": 0.9,
                "contextual_rationale": "The review praises battery duration.",
                "pipeline_mode": "rules",
            },
            {
                "review_id": "review-1",
                "product_name": "Ace Elec Power Bank",
                "product_url": "https://www.jumia.com.ng/product.html",
                "sku": "AC431EA7LKZHVNAFAMZ",
                "review_title": "Good product",
                "review_text": "The battery lasts long and delivery was fast.",
                "star_rating": 5,
                "review_date": "09-06-2026",
                "reviewer_name": "Ada",
                "verified_purchase": True,
                "source_url": "https://www.jumia.com.ng/reviews",
                "scraped_at": "2026-06-10T08:00:00+00:00",
                "cleaned_text": "The battery lasts long and delivery was fast.",
                "product_category": "Power Bank",
                "aspect": "Delivery speed",
                "aspect_category": "Delivery speed",
                "aspect_evidence": "delivery was fast",
                "vader_compound": 0.72,
                "vader_label": "positive",
                "contextual_sentiment": "positive",
                "contextual_sentiment_score": 0.8,
                "contextual_rationale": "The review praises delivery speed.",
                "pipeline_mode": "rules",
            },
        ]
    ).to_csv(output, index=False)
