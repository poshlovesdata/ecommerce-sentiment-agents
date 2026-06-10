"""Build canonical raw and processed datasets for the dashboard."""

import argparse
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jumia_aspect_agents.agents.pipeline import AspectSentimentPipeline  # noqa: E402
from jumia_aspect_agents.data_collection.dataset import (  # noqa: E402
    PROCESSED_LATEST_STEM,
    RAW_MASTER_STEM,
    build_raw_master_dataset,
    discover_raw_csv_files,
    write_processed_latest,
)
from jumia_aspect_agents.utils.logging import configure_logging  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge raw Jumia scrape batches and optionally build latest processed data."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw scrape CSV files.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory for processed latest outputs.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        default=None,
        help="Specific raw CSV file to include. Can be passed multiple times.",
    )
    parser.add_argument(
        "--mode",
        choices=["rules", "llm"],
        default=None,
        help="Optionally run the NLP pipeline after building the raw master dataset.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional review limit when running the NLP pipeline.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Loguru log level.",
    )
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

    input_files = args.input or discover_raw_csv_files(args.raw_dir)
    master_csv = args.raw_dir / f"{RAW_MASTER_STEM}.csv"
    master_json = args.raw_dir / f"{RAW_MASTER_STEM}.json"
    dataframe, output_csv, output_json = build_raw_master_dataset(
        input_files=input_files,
        output_csv=master_csv,
        output_json=master_json,
    )

    logger.success("Raw master reviews: {}", len(dataframe))
    logger.success("Raw master CSV: {}", output_csv)
    logger.success("Raw master JSON: {}", output_json)

    if args.mode:
        pipeline = AspectSentimentPipeline(mode=args.mode)
        _, processed_csv, processed_json = pipeline.process_file(
            master_csv,
            output_dir=args.processed_dir,
            limit=args.limit,
        )
        latest_csv = args.processed_dir / f"{PROCESSED_LATEST_STEM}.csv"
        latest_json = args.processed_dir / f"{PROCESSED_LATEST_STEM}.json"
        write_processed_latest(
            source_csv=processed_csv,
            source_json=processed_json,
            output_csv=latest_csv,
            output_json=latest_json,
        )
        logger.success("Latest processed CSV: {}", latest_csv)
        logger.success("Latest processed JSON: {}", latest_json)


if __name__ == "__main__":
    main()
