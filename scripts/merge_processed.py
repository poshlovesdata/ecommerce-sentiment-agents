"""Merge rules and LLM processed datasets into one dashboard dataset."""

import argparse
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jumia_aspect_agents.data_collection.dataset import (  # noqa: E402
    PROCESSED_LATEST_STEM,
    PROCESSED_MERGED_STEM,
    latest_processed_csv,
    merge_processed_datasets,
    write_processed_latest,
)
from jumia_aspect_agents.utils.logging import configure_logging  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge processed rules and LLM datasets for dashboard comparison."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory containing processed CSV files.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        default=None,
        help="Specific processed CSV file to merge. Can be passed multiple times.",
    )
    parser.add_argument(
        "--latest-modes",
        nargs="+",
        default=["rules", "llm"],
        help="Pipeline modes whose latest processed CSVs should be merged when --input is omitted.",
    )
    parser.add_argument(
        "--publish-latest",
        action="store_true",
        help="Also copy the merged dataset to jumia_reviews_processed_latest.csv/json.",
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

    input_files = args.input or [
        latest_processed_csv(args.processed_dir, mode=mode) for mode in args.latest_modes
    ]
    merged_csv = args.processed_dir / f"{PROCESSED_MERGED_STEM}.csv"
    merged_json = args.processed_dir / f"{PROCESSED_MERGED_STEM}.json"
    dataframe, output_csv, output_json = merge_processed_datasets(
        input_files=input_files,
        output_csv=merged_csv,
        output_json=merged_json,
    )

    logger.success("Merged processed rows: {}", len(dataframe))
    logger.success("Merged CSV: {}", output_csv)
    logger.success("Merged JSON: {}", output_json)

    if args.publish_latest:
        latest_csv = args.processed_dir / f"{PROCESSED_LATEST_STEM}.csv"
        latest_json = args.processed_dir / f"{PROCESSED_LATEST_STEM}.json"
        write_processed_latest(
            source_csv=output_csv,
            source_json=output_json,
            output_csv=latest_csv,
            output_json=latest_json,
        )
        logger.success("Published latest CSV: {}", latest_csv)
        logger.success("Published latest JSON: {}", latest_json)


if __name__ == "__main__":
    main()
