"""Create a stratified raw review sample for cost-controlled LLM processing."""

import argparse
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jumia_aspect_agents.data_collection.dataset import (  # noqa: E402
    RAW_LLM_SAMPLE_STEM,
    RAW_MASTER_STEM,
    sample_raw_reviews,
)
from jumia_aspect_agents.utils.logging import configure_logging  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a deterministic raw review sample spread across products and ratings."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw") / f"{RAW_MASTER_STEM}.csv",
        help="Raw master CSV to sample from.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory where sample CSV/JSON files will be written.",
    )
    parser.add_argument(
        "--output-stem",
        default=RAW_LLM_SAMPLE_STEM,
        help="Output filename stem without extension.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=300,
        help="Maximum number of raw reviews to include in the sample.",
    )
    parser.add_argument(
        "--group-by",
        nargs="+",
        default=["product_name", "star_rating"],
        help="Columns used to spread the sample across groups.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Deterministic random seed used to shuffle each group.",
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

    output_csv = args.output_dir / f"{args.output_stem}.csv"
    output_json = args.output_dir / f"{args.output_stem}.json"
    dataframe, csv_path, json_path = sample_raw_reviews(
        input_csv=args.input,
        output_csv=output_csv,
        output_json=output_json,
        sample_size=args.sample_size,
        group_columns=args.group_by,
        random_state=args.random_state,
    )

    logger.success("Sampled raw reviews: {}", len(dataframe))
    logger.success("Unique products: {}", dataframe["product_name"].nunique())
    if "star_rating" in dataframe.columns:
        logger.success("Star ratings: {}", sorted(dataframe["star_rating"].dropna().unique()))
    logger.success("Sample CSV: {}", csv_path)
    logger.success("Sample JSON: {}", json_path)


if __name__ == "__main__":
    main()
