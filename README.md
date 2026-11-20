FINM 32800 Final Project: Factor Timing
=======================================

## About this project

Factor timing paper replication

## Quick Start

The quickest way to run code in this repo is to use the following steps.

To compile the LaTeX reports you need TexLive (or another LaTeX distribution) installed on your computer and available in your path.
You can do this by downloading and installing it from here ([windows](https://tug.org/texlive/windows.html#install)
and [mac](https://tug.org/mactex/mactex-download.html) installers). Without it, the rest of the project
still builds, and `doit` says that the reports were not compiled.


This project uses [uv](https://docs.astral.sh/uv/) for dependency management. First, install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then sync the environment and activate it, so that the commands below find its tools:
```bash
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Finally, run the project tasks:
```bash
chartbook run
```
`chartbook run` runs `doit` (every task in `dodo.py` but the tests), whose final task renders
the documentation site into `docs/`. Open it with `chartbook docs open`.
And that's it!


### Other commands

#### Unit Tests and Doc Tests

You can run the unit test, including doctests, with the following command:
```
pytest --doctest-modules
```
`doit run_pytest` runs the tests as a task, and saves the results in `_output`.
A plain `doit` does not run them.

You can render the documentation site, without running anything, with:
```
chartbook docs build -f
```
`chartbook run` runs `doit`, including its final documentation task, and `chartbook check`
says what `chartbook.toml` is missing.


#### Setting Environment Variables

You can [export your environment variables](https://stackoverflow.com/questions/43267413/how-to-set-environment-variables-from-env-file)
from your `.env` files like so, if you wish. This can be done easily in a Linux or Mac terminal with the following command:
```bash
set -a  # automatically export all variables
source .env
set +a
```
On Windows (PowerShell):
```powershell
Get-Content .env | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }
```

### Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting Python code.

```bash
# Auto-fix linting issues (e.g., unused imports, undefined names)
ruff check . --fix

# Format code (consistent style, spacing, line length)
ruff format .

# Sort imports, then fix linting issues, then format
ruff format . && ruff check --select I --fix . && ruff check --fix .
```

- `ruff check --fix` applies safe auto-fixes for linting violations
- `ruff format` formats code similar to Black
- `--select I` targets only import sorting rules (isort-compatible)

### General Directory Structure

 - The `assets` folder is used for things like hand-drawn figures or other
   pictures that were not generated from code. These things cannot be easily
   recreated if they are deleted.

 - The `_output` folder, on the other hand, contains dataframes and figures that are
   generated from code. The entire folder should be able to be deleted, because
   the code can be run again, which would again generate all of the contents.

 - The `data_manual` is for data that cannot be easily recreated. This data
   should be version controlled. Anything in the `_data` folder or in
   the `_output` folder should be able to be recreated by running the code
   and can safely be deleted.

 - I'm using the `doit` Python module as a task runner. It works like `make` and
   the associated `Makefile`s. To rerun the code, install `doit`
   (https://pydoit.org/) and execute the command `doit` in the project's
   folder, where `dodo.py` is. Note that doit is very flexible and can be used to run code
   commands from the command prompt, thus making it suitable for projects that
   use scripts written in multiple different programming languages.

 - I'm using the `.env` file as a container for absolute paths that are private
   to each collaborator in the project. You can also use it for private
   credentials, if needed. It should not be tracked in Git. That is all it
   holds: secrets and machine facts (API keys, `WRDS_USERNAME`, `DATA_DIR`).
   Anything that changes what is computed lives in a committed file, so that
   two people with different `.env` files who build the same commit get the
   same bytes. The data window, `START_DATE` and `END_DATE`, is committed in
   `src/settings.py`; `END_DATE` is the pipeline's cutoff, and moving it is a
   commit.

### Data and Output Storage

I'll often use a separate folder for storing data. Any data in the data folder
can be deleted and recreated by rerunning the PyDoit command (the pulls are in
the dodo.py file). Any data that cannot be automatically recreated should be
stored in the "data_manual" folder. Because of the risk of manually-created data
getting changed or lost, I prefer to keep it under version control if I can.
Thus, data in the "_data" folder is excluded from Git (see the .gitignore file),
while the "data_manual" folder is tracked by Git.

Output is stored in the "_output" directory. This includes dataframes, charts, and
rendered notebooks. When the output is small enough, I'll keep this under
version control. I like this because I can keep track of how dataframes change as my
analysis progresses, for example.

Of course, the _data directory and _output directory can be kept elsewhere on the
machine. To make this easy, I always include the ability to customize these
locations by defining the path to these directories in environment variables,
which I intend to be defined in the `.env` file, though they can also simply be
defined on the command line or elsewhere. The `settings.py` is responsible for
loading these environment variables and doing some preprocessing on them.
The `settings.py` file is the entry point for all other scripts to these
definitions. That is, all code that references these variables and others are
loaded by importing `config`.

### Naming Conventions

 - **`pull_` vs `load_`**: Files or functions that pull data from an external
 data source are prepended with "pull_", as in "pull_fred.py". Functions that
 load data that has been cached in the "_data" folder are prepended with "load_".
 For example, inside of the `pull_CRSP_Compustat.py` file there is both a
 `pull_compustat` function and a `load_compustat` function. The first pulls from
 the web, whereas the other loads cached data from the "_data" directory.


### Dependencies and Virtual Environments

#### Working with `uv`

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management. Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

To sync your environment with the lockfile:
```bash
uv sync
```

To run a command in it without activating it first, put `uv run` before it:
```bash
uv run chartbook run
```

To add a new dependency:
```bash
uv add <package-name>
```

To update all dependencies:
```bash
uv lock --upgrade
uv sync
```

