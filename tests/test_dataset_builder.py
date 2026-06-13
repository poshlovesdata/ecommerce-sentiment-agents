"""Tests for canonical dataset building."""

from datetime import datetime, timezone

import pandas as pd

from jumia_aspect_agents.data_collection.dataset import (
    build_raw_master_dataset,
    discover_raw_csv_files,
    latest_processed_csv,
    merge_processed_datasets,
    sample_raw_reviews,
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


def processed_row(pipeline_mode: str, aspect: str) -> dict:
    return {
        "review_id": "review-1",
        "product_name": "Ace Elec Power Bank",
        "review_date": "09-06-2026",
        "aspect": aspect,
        "aspect_category": aspect,
        "aspect_evidence": aspect.lower(),
        "pipeline_mode": pipeline_mode,
        "contextual_sentiment": "positive",
    }


def test_latest_processed_csv_returns_latest_matching_mode(tmp_path) -> None:
    older = tmp_path / "jumia_reviews_processed_20260610_rules.csv"
    newer = tmp_path / "jumia_reviews_processed_20260611_rules.csv"
    other = tmp_path / "jumia_reviews_processed_20260611_llm.csv"
    latest = tmp_path / "jumia_reviews_processed_latest.csv"
    for path in [older, newer, other, latest]:
        pd.DataFrame([processed_row("rules", "Battery life")]).to_csv(path, index=False)

    assert latest_processed_csv(tmp_path, mode="rules") == newer


def test_merge_processed_datasets_preserves_pipeline_modes(tmp_path) -> None:
    rules = tmp_path / "jumia_reviews_processed_master_rules.csv"
    llm = tmp_path / "jumia_reviews_processed_master_llm.csv"
    pd.DataFrame([processed_row("rules", "Battery life")]).to_csv(rules, index=False)
    pd.DataFrame([processed_row("llm", "Battery life")]).to_csv(llm, index=False)

    dataframe, output_csv, output_json = merge_processed_datasets(
        input_files=[rules, llm],
        output_csv=tmp_path / "jumia_reviews_processed_merged.csv",
        output_json=tmp_path / "jumia_reviews_processed_merged.json",
    )

    assert len(dataframe) == 2
    assert set(dataframe["pipeline_mode"]) == {"rules", "llm"}
    assert output_csv.exists()
    assert output_json.exists()


def test_sample_raw_reviews_spreads_across_products_and_ratings(tmp_path) -> None:
    input_csv = tmp_path / "jumia_reviews_raw_master.csv"
    rows = []
    timestamp = datetime.now(timezone.utc).isoformat()
    for product_index in range(4):
        for rating in [1, 5]:
            for review_index in range(3):
                row = raw_row(
                    f"Review {product_index}-{rating}-{review_index}",
                    timestamp,
                )
                row["product_name"] = f"Product {product_index}"
                row["product_url"] = f"https://www.jumia.com.ng/product-{product_index}.html"
                row["star_rating"] = rating
                row["reviewer_name"] = f"Reviewer {review_index}"
                rows.append(row)
    pd.DataFrame(rows).to_csv(input_csv, index=False)

    sample, output_csv, output_json = sample_raw_reviews(
        input_csv=input_csv,
        output_csv=tmp_path / "jumia_reviews_raw_llm_stratified_sample.csv",
        output_json=tmp_path / "jumia_reviews_raw_llm_stratified_sample.json",
        sample_size=8,
        group_columns=["product_name", "star_rating"],
        random_state=7,
    )

    assert len(sample) == 8
    assert sample["product_name"].nunique() == 4
    assert set(sample["star_rating"]) == {1, 5}
    assert output_csv.exists()
    assert output_json.exists()
