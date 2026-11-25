"""Tests for data_manual/anomaly_map.csv: the paper's 50 anomalies and Kozak's names.

The first test reads only the committed CSV, so it runs everywhere. The second
also needs Kozak's data in DATA_DIR and is skipped until `doit pull_kozak` has run.
"""

from pathlib import Path

import pandas as pd
import pytest

import pull_kozak
from settings import config

DATA_DIR = Path(config("DATA_DIR"))
MANUAL_DATA_DIR = Path(config("MANUAL_DATA_DIR"))
FT_FOLDER = DATA_DIR / pull_kozak.FT_DIRNAME / pull_kozak.FT_CSV_SUBDIR

COLUMNS = [
    "paper_order",
    "paper_name",
    "kozak_name",
    "long_leg",
    "definition",
    "inputs",
    "notes",
]
REQUIRED = COLUMNS[:-1]  # every column but notes
NOT_IN_PAPER = {"divp", "divg", "exchsw", "invaci", "ipo"}


def load_map():
    return pd.read_csv(MANUAL_DATA_DIR / "anomaly_map.csv")


def test_map_shape_and_fields():
    df = load_map()
    assert list(df.columns) == COLUMNS
    assert len(df) == 50
    assert df["paper_order"].tolist() == list(range(1, 51))
    assert df["paper_name"].is_unique
    assert df["kozak_name"].is_unique
    assert set(df["long_leg"]) <= {"high", "low", "check"}
    for col in REQUIRED:
        empty = df[col].isna() | df[col].astype(str).str.strip().eq("")
        rows = df.loc[empty, "paper_order"].tolist()
        assert not empty.any(), f"empty {col} in rows {rows}"


@pytest.mark.skipif(
    not (FT_FOLDER / "ret10_size.csv").exists(),
    reason="needs the Factor Timing data: run `doit pull_kozak` first",
)
def test_kozak_names_exist():
    kozak = set(pull_kozak.load_ft_anomalies(DATA_DIR))
    mapped = set(load_map()["kozak_name"])
    assert mapped <= kozak, f"not in Kozak's files: {sorted(mapped - kozak)}"
    assert kozak - mapped == NOT_IN_PAPER
