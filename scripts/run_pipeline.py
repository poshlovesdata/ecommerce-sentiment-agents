"""CLI entrypoint for the aspect-based NLP pipeline."""

import argparse
import os
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jumia_aspect_agents.agents.pipeline import AspectSentimentPipeline  # noqa: E402
from jumia_aspect_agents.config import settings  # noqa: E402
from jumia_aspect_agents.utils.logging import configure_logging  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process raw Jumia reviews into aspect-level sentiment rows."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Raw CSV or JSON file from scripts/scrape_jumia.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory where processed CSV/JSON files will be written.",
    )
    parser.add_argument(
        "--mode",
        choices=["rules", "llm"],
        default="rules",
        help="Use deterministic local rules or PydanticAI/OpenAI agents.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of raw reviews to process for testing.",
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

    if args.mode == "llm" and not (os.getenv("OPENAI_API_KEY") or settings.openai_api_key):
        raise SystemExit("OPENAI_API_KEY must be set when --mode llm is used.")

    pipeline = AspectSentimentPipeline(mode=args.mode)
    records, output_csv, output_json = pipeline.process_file(
        args.input,
        output_dir=args.output_dir,
        limit=args.limit,
    )
    logger.success("Processed aspect rows: {}", len(records))
    logger.success("CSV: {}", output_csv)
    logger.success("JSON: {}", output_json)


if __name__ == "__main__":
    main()
