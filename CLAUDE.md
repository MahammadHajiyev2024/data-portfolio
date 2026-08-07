# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

This is a data portfolio repo: a collection of independent, numbered project folders (e.g. `01-analytics-pipeline-duckdb`), each a self-contained Python project with its own `pyproject.toml`, `uv.lock`, and `README.md`. There is no shared root-level package, build config, or dependency set — treat each numbered folder as its own project and `cd` into it before running any commands.

## Tooling

Each project uses [uv](https://docs.astral.sh/uv/) for dependency management and requires Python 3.14+ (pinned via `.python-version`).

Common commands, run from within a project folder (e.g. `01-analytics-pipeline-duckdb/`):

```bash
uv sync          # install dependencies from pyproject.toml / uv.lock
uv run main.py   # run the project's entry point
```

## 01-analytics-pipeline-duckdb

A small ELT pipeline that pulls macroeconomic indicators from FRED (Federal Reserve Economic Data) into a local DuckDB file.

- `main.py` — orchestrates the pipeline: `init_db()` → `extract_fred_data()` → `transform_and_load()`.
- `src/database.py` — owns the DuckDB connection and schema DDL. `DB_PATH` is resolved relative to `__file__`, always pointing at `<project_root>/data/macro_analytics.duckdb` regardless of cwd. Two tables: `staging_macro_indicators` (unused currently) and `fact_macro_metrics` (the production table, keyed on `metric_date`).
- `src/ingestion.py` — `extract_fred_data(symbols)` downloads raw CSVs directly from FRED's public graph endpoint (`fred.stlouisfed.org/graph/fredgraph.csv?id=<symbol>`, no API key), then `transform_and_load()` cleans/forward-fills the data in pandas and does an idempotent `INSERT OR REPLACE` upsert into `fact_macro_metrics` via DuckDB. Data is filtered to 2023-01-01 onward.
- `notebooks/01_eda_and_exploration.ipynb` — exploratory analysis/visualization against the DuckDB file; not part of the pipeline run path.
- `data/macro_analytics.duckdb` is a generated/binary artifact (checked into the repo) — treat it as pipeline output, not source of truth to hand-edit.

Adding a new indicator: append its FRED series ID to the `symbols` list in `main.py`, then extend the column mapping in `transform_and_load` and the `fact_macro_metrics` schema in `database.py`.

## Adding a new project

Follow the existing numbering convention (`NN-short-description`) and scaffold it as an independent `uv` project (`uv init`) rather than adding it to a shared/monorepo dependency set.
