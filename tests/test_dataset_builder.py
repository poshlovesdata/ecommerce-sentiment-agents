"""Tests for canonical dataset building."""

from datetime import datetime, timezone

import pandas as pd

from jumia_aspect_agents.data_collection.dataset import (
    build_raw_master_dataset,
    discover_raw_csv_files,
)


def raw_row(review_body: str, scraped_at: str) -> dict:
    return {
        "product_name": "Ace Elec Power Bank",
        "product_url": "https://www.jumia.com.ng/product.html",
        "sku": "AC431EA7LKZHVNAFAMZ",
        "review_title": "good",
        "review_body": review_body,
        "star_rating": 5,
        "review_date": "09-06-2026",
        "reviewer_name": "Ada",
        "verified_purchase": True,
        "source_url": "https://www.jumia.com.ng/reviews",
        "scraped_at": scraped_at,
    }


def test_discover_raw_csv_files_excludes_master(tmp_path) -> None:
    raw_file = tmp_path / "jumia_reviews_raw_20260610_000000.csv"
    master_file = tmp_path / "jumia_reviews_raw_master.csv"
    raw_file.write_text("x\n", encoding="utf-8")
    master_file.write_text("x\n", encoding="utf-8")

    assert discover_raw_csv_files(tmp_path) == [raw_file]


def test_build_raw_master_dataset_dedupes_reviews(tmp_path) -> None:
    first = tmp_path / "jumia_reviews_raw_1.csv"
    second = tmp_path / "jumia_reviews_raw_2.csv"
    timestamp = datetime.now(timezone.utc).isoformat()
    pd.DataFrame([raw_row("Nice and portable", timestamp)]).to_csv(first, index=False)
    pd.DataFrame([raw_row("Nice and portable", timestamp)]).to_csv(second, index=False)

    dataframe, output_csv, output_json = build_raw_master_dataset(
        input_files=[first, second],
        output_csv=tmp_path / "jumia_reviews_raw_master.csv",
        output_json=tmp_path / "jumia_reviews_raw_master.json",
    )

    assert len(dataframe) == 1
    assert output_csv.exists()
    assert output_json.exists()
    assert "review_id" in dataframe.columns
