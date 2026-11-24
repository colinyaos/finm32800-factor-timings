"""Pull Serhiy Kozak's published code and data into DATA_DIR.

Two sources:

- The SCS repository (https://github.com/serhiykozak/SCS), the replication
  code and data for Kozak, Nagel and Santosh (2020) "Shrinking the
  Cross-Section". Kept as a reference copy in ``DATA_DIR / "kozak_scs"``,
  checked out at a fixed commit so every clone is the same.
- The monthly data for Haddad, Kozak and Santosh (2020) "Factor Timing",
  from Kozak's data page (https://serhiykozak.com/data-code). It is a .7z
  archive, extracted into ``DATA_DIR / "kozak_ft_monthly"``.

The Factor Timing folder holds four files for each of 55 anomalies
(``ret10_ANOM.csv`` and so on), each with columns ``date, p1, ..., p10``,
p1 the short and p10 the long decile:

- ``ret10``: monthly value-weighted decile returns, 1963-07 to 2018-06
- ``bmc10``: monthly decile book-to-market ratios
- ``totalme10``: monthly decile total market capitalization
- ``n10``: number of firms per decile, *daily*

Some anomalies start later (up to 1973-10) or end early (2018-01 or
2018-03), and a few (ipo, repurch, debtiss, exchsw, fscore) are mostly empty.

Follows the project convention: ``pull_*`` hits the network and, as a
script, caches to ``DATA_DIR``; ``load_*`` reads the cache.
"""

import subprocess
from pathlib import Path

import pandas as pd
import py7zr
import requests

from settings import config

DATA_DIR = config("DATA_DIR")

SCS_REPO_URL = "https://github.com/serhiykozak/SCS"
SCS_COMMIT = "f0959e98c0b4022e24dcede00f48f40789d7ab27"  # master on 2025-01-01
SCS_DIRNAME = "kozak_scs"

FT_MONTHLY_URL = "https://serhiykozak.com/data/FT-17APR19-monthly.7z"
FT_ARCHIVE_NAME = "FT-17APR19-monthly.7z"
FT_DIRNAME = "kozak_ft_monthly"
FT_CSV_SUBDIR = "FT-17APR19-monthly"  # folder inside the archive
FT_KINDS = ("ret10", "bmc10", "totalme10", "n10")


def pull_scs_repo(data_dir=DATA_DIR, commit=SCS_COMMIT):
    """Clone the SCS repo into ``data_dir / "kozak_scs"`` and check out ``commit``."""
    dest = Path(data_dir) / SCS_DIRNAME
    if not dest.exists():
        subprocess.run(["git", "clone", SCS_REPO_URL, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--quiet", commit], check=True)
    return dest


def pull_factor_timing_monthly(data_dir=DATA_DIR):
    """Download the Factor Timing monthly archive and extract it."""
    data_dir = Path(data_dir)
    archive = data_dir / FT_ARCHIVE_NAME
    response = requests.get(FT_MONTHLY_URL, timeout=120)
    response.raise_for_status()
    archive.write_bytes(response.content)
    with py7zr.SevenZipFile(archive, mode="r") as z:
        z.extractall(path=data_dir / FT_DIRNAME)
    return data_dir / FT_DIRNAME


def load_ft_anomalies(data_dir=DATA_DIR):
    """The 55 anomaly names in the cached Factor Timing data, sorted."""
    folder = Path(data_dir) / FT_DIRNAME / FT_CSV_SUBDIR
    return sorted(f.stem.removeprefix("ret10_") for f in folder.glob("ret10_*.csv"))


def load_ft_portfolios(anomaly, kind="ret10", data_dir=DATA_DIR):
    """Load one Factor Timing file: ``date`` plus deciles ``p1``-``p10``.

    ``kind`` is one of ``FT_KINDS``. Monthly dates (``MM/YYYY``) parse to the
    first of the month; the daily ``n10`` dates parse to the day.
    """
    if kind not in FT_KINDS:
        raise ValueError(f"kind must be one of {FT_KINDS}, not {kind!r}")
    path = Path(data_dir) / FT_DIRNAME / FT_CSV_SUBDIR / f"{kind}_{anomaly}.csv"
    df = pd.read_csv(path)
    date_format = "%m/%d/%Y" if kind == "n10" else "%m/%Y"
    df["date"] = pd.to_datetime(df["date"], format=date_format)
    return df


def load_scs_data(filename, data_dir=DATA_DIR):
    """Load one CSV from the reference SCS repo's ``Data`` folder, as is."""
    return pd.read_csv(Path(data_dir) / SCS_DIRNAME / "Data" / filename)


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"SCS repo at {pull_scs_repo()}")
    print(f"Factor Timing monthly data at {pull_factor_timing_monthly()}")
