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
PROCESSED_MERGED_STEM = "jumia_reviews_processed_merged"


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


def discover_processed_csv_files(processed_dir: Path, mode: str | None = None) -> list[Path]:
    """Return timestamped processed CSVs, optionally filtered by pipeline mode."""

    files = [
        path
        for path in processed_dir.glob("jumia_reviews_processed_*.csv")
        if path.stem not in {PROCESSED_LATEST_STEM, PROCESSED_MERGED_STEM}
    ]
    if mode is not None:
        files = [path for path in files if path.stem.endswith(f"_{mode}")]
    return sorted(files)


def latest_processed_csv(processed_dir: Path, mode: str) -> Path:
    """Return the latest processed CSV for a pipeline mode."""

    files = discover_processed_csv_files(processed_dir, mode=mode)
    if not files:
        raise ValueError(f"No processed {mode!r} CSV files were found in {processed_dir}.")
    return files[-1]


def merge_processed_datasets(
    *,
    input_files: list[Path],
    output_csv: Path,
    output_json: Path,
) -> tuple[pd.DataFrame, Path, Path]:
    """Merge processed rules/LLM datasets for dashboard comparison."""

    if not input_files:
        raise ValueError("No processed CSV files were provided.")

    frames = []
    for path in input_files:
        logger.info("Loading processed file {}", path)
        dataframe = pd.read_csv(path)
        if dataframe.empty:
            logger.warning("Skipping processed file with no rows {}", path)
            continue
        if "pipeline_mode" not in dataframe.columns:
            raise ValueError(f"Processed file is missing pipeline_mode column: {path}")
        frames.append(dataframe)

    if not frames:
        raise ValueError("No non-empty processed CSV files were available to merge.")

    merged = pd.concat(frames, ignore_index=True)
    dedupe_columns = [
        column
        for column in ["review_id", "pipeline_mode", "aspect", "aspect_category", "aspect_evidence"]
        if column in merged.columns
    ]
    before = len(merged)
    if dedupe_columns:
        merged = merged.drop_duplicates(subset=dedupe_columns, keep="last")
    merged = merged.sort_values(
        [column for column in ["pipeline_mode", "product_name", "review_date", "aspect"] if column in merged],
        na_position="last",
    ).reset_index(drop=True)
    after = len(merged)
    logger.info("Merged {} processed rows into {} deduplicated rows", before, after)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_csv, index=False)

    with output_json.open("w", encoding="utf-8") as file:
        json.dump(merged.to_dict(orient="records"), file, ensure_ascii=False, indent=2)

    return merged, output_csv, output_json


def records(dataframe: pd.DataFrame) -> list[dict]:
    """Return dataframe rows as dictionaries with null-like values normalized."""

    return dataframe.where(pd.notna(dataframe), None).to_dict(orient="records")
