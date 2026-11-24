"""Tests for the cached Factor Timing data pulled by ``pull_kozak.py``.

They read files in DATA_DIR, so they are skipped until `doit pull_kozak`
has run (as in GitHub Actions, where there is no data).
"""

from pathlib import Path

import pandas as pd
import pytest

import pull_kozak
from settings import config

DATA_DIR = Path(config("DATA_DIR"))
FT_FOLDER = DATA_DIR / pull_kozak.FT_DIRNAME / pull_kozak.FT_CSV_SUBDIR

pytestmark = pytest.mark.skipif(
    not (FT_FOLDER / "ret10_size.csv").exists(),
    reason="needs the Factor Timing data: run `doit pull_kozak` first",
)

DECILES = [f"p{i}" for i in range(1, 11)]


def test_columns():
    anomalies = pull_kozak.load_ft_anomalies(DATA_DIR)
    assert len(anomalies) == 55
    for kind in pull_kozak.FT_KINDS:
        df = pull_kozak.load_ft_portfolios("size", kind, DATA_DIR)
        assert list(df.columns) == ["date", *DECILES], kind


def test_date_range():
    for kind in ("ret10", "bmc10", "totalme10"):
        df = pull_kozak.load_ft_portfolios("size", kind, DATA_DIR)
        assert df["date"].min() == pd.Timestamp("1963-07-01"), kind
        assert df["date"].max() == pd.Timestamp("2018-06-01"), kind
        assert len(df) == 660, f"{kind}: one row per month"


def test_no_duplicate_dates():
    for anomaly in pull_kozak.load_ft_anomalies(DATA_DIR):
        for kind in ("ret10", "bmc10"):
            df = pull_kozak.load_ft_portfolios(anomaly, kind, DATA_DIR)
            assert not df["date"].duplicated().any(), f"{kind}_{anomaly}"
