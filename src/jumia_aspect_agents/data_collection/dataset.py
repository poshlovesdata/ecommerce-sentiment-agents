"""Dataset management helpers for raw scraped review batches."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError
from loguru import logger

from jumia_aspect_agents.agents.pipeline import make_review_id
from jumia_aspect_agents.models.reviews import RawReview


RAW_MASTER_STEM = "jumia_reviews_raw_master"
PROCESSED_LATEST_STEM = "jumia_reviews_processed_latest"


def discover_raw_csv_files(raw_dir: Path) -> list[Path]:
    """Return timestamped raw scrape CSVs, excluding master files."""

    return sorted(
        path
        for path in raw_dir.glob("jumia_reviews_raw_*.csv")
        if path.stem != RAW_MASTER_STEM
    )


def build_raw_master_dataset(
    *,
    input_files: list[Path],
    output_csv: Path,
    output_json: Path,
) -> tuple[pd.DataFrame, Path, Path]:
    """Merge raw scrape files, dedupe reviews, and write master CSV/JSON outputs."""

    if not input_files:
        raise ValueError("No raw CSV files were provided.")

    frames = []
    for path in input_files:
        logger.info("Loading raw scrape file {}", path)
        try:
            dataframe = pd.read_csv(path)
        except EmptyDataError:
            logger.warning("Skipping empty raw scrape file {}", path)
            continue
        if dataframe.empty:
            logger.warning("Skipping raw scrape file with no rows {}", path)
            continue
        frames.append(dataframe)

    if not frames:
        raise ValueError("No non-empty raw CSV files were available to merge.")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.where(pd.notna(combined), None)
    combined["review_id"] = [make_review_id(RawReview.model_validate(row)) for row in records(combined)]

    before = len(combined)
    deduped = (
        combined.sort_values(["scraped_at", "source_url"], na_position="last")
        .drop_duplicates(subset=["review_id"], keep="last")
        .sort_values(["product_name", "review_date", "reviewer_name"], na_position="last")
        .reset_index(drop=True)
    )
    after = len(deduped)
    logger.info("Merged {} rows into {} deduplicated reviews", before, after)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    deduped.to_csv(output_csv, index=False)

    with output_json.open("w", encoding="utf-8") as file:
        json.dump(deduped.to_dict(orient="records"), file, ensure_ascii=False, indent=2)

    return deduped, output_csv, output_json


def write_processed_latest(
    *,
    source_csv: Path,
    source_json: Path | None,
    output_csv: Path,
    output_json: Path,
) -> tuple[Path, Path]:
    """Copy a processed dataset to stable latest CSV/JSON paths."""

    dataframe = pd.read_csv(source_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_csv, index=False)

    if source_json and source_json.exists():
        output_json.write_text(source_json.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        with output_json.open("w", encoding="utf-8") as file:
            json.dump(dataframe.to_dict(orient="records"), file, ensure_ascii=False, indent=2)

    return output_csv, output_json


def records(dataframe: pd.DataFrame) -> list[dict]:
    """Return dataframe rows as dictionaries with null-like values normalized."""

    return dataframe.where(pd.notna(dataframe), None).to_dict(orient="records")
