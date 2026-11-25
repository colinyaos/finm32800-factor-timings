"""Run or update the project. This file uses the `doit` Python package. It works
like a Makefile, but is Python-based

"""

#######################################
## Configuration and Helpers for PyDoit
#######################################
## Make sure the src folder is in the path
import sys

sys.path.insert(1, "./src/")

import inspect
import shutil
from os import environ
from pathlib import Path

from settings import config

# Which tasks `doit` runs on its own is set at the end of this file
DOIT_CONFIG = {"backend": "sqlite3", "dep_file": "./.doit-db.sqlite"}


BASE_DIR = config("BASE_DIR")
DATA_DIR = config("DATA_DIR")
MANUAL_DATA_DIR = config("MANUAL_DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")
OS_TYPE = config("OS_TYPE")

## Helpers for handling Jupyter Notebook tasks
environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

# fmt: off
## Helper functions for automatic execution of Jupyter notebooks. Each path is quoted, for a
## project in a folder whose name has a space ("C:\Users\Jane Doe\...", "My Drive").
def jupyter_execute_notebook(notebook_path):
    return f'jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f'jupyter nbconvert --to html --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_to_md(notebook_path, output_dir=OUTPUT_DIR):
    """Requires jupytext"""
    return f'jupytext --to markdown --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_clear_output(notebook_path):
    """Clear the output of a notebook"""
    return f'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
# fmt: on


def mv(from_path, to_path):
    """Move a file to a folder"""
    from_path = Path(from_path)
    to_path = Path(to_path)
    to_path.mkdir(parents=True, exist_ok=True)
    if OS_TYPE == "nix":
        command = f'mv "{from_path}" "{to_path}"'
    else:
        command = f'move "{from_path}" "{to_path}"'
    return command


def copy_file(origin_path, destination_path, mkdir=True):
    """Create a Python action for copying a file."""

    def _copy_file():
        origin = Path(origin_path)
        dest = Path(destination_path)
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)

    return _copy_file


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for data and output if they don't exist"""
    return {
        "actions": ["python ./src/settings.py"],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": ["./src/settings.py"],
        "clean": [],
    }


def task_pull():
    """Pull data from external sources"""
    yield {
        "name": "crsp_stock",
        "doc": "Pull CRSP stock data from WRDS",
        "actions": [
            "python ./src/settings.py",
            "python ./src/pull_CRSP_stock.py",
        ],
        "targets": [DATA_DIR / "CRSP_monthly_stock.parquet", DATA_DIR / "CRSP_MSIX.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_CRSP_stock.py"],
        "clean": [],
    }
    yield {
        "name": "crsp_compustat",
        "doc": "Pull CRSP Compustat data from WRDS",
        "actions": [
            "python ./src/settings.py",
            "python ./src/pull_CRSP_Compustat.py",
        ],
        "targets": [
            DATA_DIR / "Compustat.parquet",
            DATA_DIR / "CRSP_stock_ciz.parquet",
            DATA_DIR / "CRSP_Comp_Link_Table.parquet",
            DATA_DIR / "FF_FACTORS.parquet",
        ],
        "file_dep": ["./src/settings.py", "./src/pull_CRSP_Compustat.py"],
        "clean": [],
    }


def task_pull_kozak():
    """Pull Kozak's SCS repo and the Haddad-Kozak-Santosh Factor Timing monthly data"""
    ft_dir = DATA_DIR / "kozak_ft_monthly"
    return {
        "actions": [
            "python ./src/settings.py",
            "python ./src/pull_kozak.py",
        ],
        "targets": [
            DATA_DIR / "kozak_scs" / "README.MD",
            DATA_DIR / "FT-17APR19-monthly.7z",
            ft_dir / "readme.txt",
            ft_dir / "FT-17APR19-monthly" / "ret10_size.csv",
            ft_dir / "FT-17APR19-monthly" / "bmc10_size.csv",
        ],
        "file_dep": ["./src/settings.py", "./src/pull_kozak.py"],
        "clean": [],
    }


###############################################################
## Task below is for LaTeX compilation
###############################################################


def task_compile_latex_docs():
    """Compile the LaTeX documents to PDFs"""
    file_dep = [
        "./reports/report.tex",
        "./reports/my_article_header.sty",
        "./reports/my_common_header.sty",
        "./reports/bibliography.bib",
    ]
    targets = ["./reports/report.pdf"]

    if shutil.which("latexmk") is None:
        # Without TeX, the rest of the project still builds
        def say_latex_not_found():
            print(
                "latexmk was not found, so the reports in ./reports are not compiled. "
                "Install TeX Live (https://tug.org/texlive/), then run `doit compile_latex_docs`.",
                file=sys.stderr,
            )

        return {
            "actions": [say_latex_not_found],
            "targets": targets,
            "file_dep": file_dep,
        }

    return {
        "actions": [
            "latexmk -xelatex -halt-on-error -cd ./reports/report.tex",  # Compile
            "latexmk -xelatex -halt-on-error -c -cd ./reports/report.tex",  # Clean
        ],
        "targets": targets,
        "file_dep": file_dep,
        "clean": True,
    }


def task_run_pytest():
    """Run pytest and save results to OUTPUT_DIR"""
    src_py_files = list(Path("./src").glob("*.py"))
    test_output = OUTPUT_DIR / "pytest_results.xml"

    def run_pytest():
        import subprocess

        result = subprocess.run(
            ["pytest", f"--junitxml={test_output}"],
        )
        if result.returncode != 0:
            # Remove the XML so doit won't consider the target up-to-date
            Path(test_output).unlink(missing_ok=True)
            raise RuntimeError(f"pytest failed with exit code {result.returncode}")

    return {
        "actions": [run_pytest],
        "targets": [test_output],
        "file_dep": src_py_files,
        "clean": True,
        "verbosity": 2,
    }



def task_chartbook_docs():
    """Render the pipeline site after its data and charts have been built."""
    return {
        "actions": ["chartbook docs build -f"],
        "task_dep": [name for name in _doit_tasks(globals()) if name not in ("chartbook_docs", "run_pytest")],
        "verbosity": 2,
    }




## `doit` on its own (and so `chartbook run`) runs every task in this file
## but the tests, which run with `doit run_pytest`.
##
## This block must stay the last thing in the file. It lists the tasks
## defined above it, as the file is read, so a task added below it is not
## in the list: plain `doit` and `chartbook run` do not run it, and what
## it makes is not built. A task is what doit takes for one: a function whose
## name starts with `task_` (or a method), defined here or imported, or
## anything with a `create_doit_tasks`; but not doit's own `task_params`.
try:
    from doit import task_params as _doit_task_params
except ImportError:
    _doit_task_params = None


def _doit_tasks(namespace):
    """The names of the tasks doit finds in this file, by its own rule."""
    for name, value in list(namespace.items()):
        if value is _doit_task_params:
            continue
        if name.startswith("task_") and (inspect.isfunction(value) or inspect.ismethod(value)):
            yield name.removeprefix("task_")
        elif hasattr(value, "create_doit_tasks"):
            yield getattr(value.create_doit_tasks, "basename", name)


DOIT_CONFIG["default_tasks"] = [name for name in _doit_tasks(globals()) if name != "run_pytest"]
