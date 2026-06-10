"""File output helpers for collected and processed datasets."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel


def model_records_to_dicts(records: list[BaseModel]) -> list[dict[str, Any]]:
    """Convert Pydantic records into JSON-serializable dictionaries."""

    return [record.model_dump(mode="json") for record in records]


def write_records_csv_json(
    records: list[BaseModel],
    *,
    csv_path: Path,
    json_path: Path,
) -> tuple[Path, Path]:
    """Write records to both CSV and JSON for research reproducibility."""

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    rows = model_records_to_dicts(records)
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return csv_path, json_path
