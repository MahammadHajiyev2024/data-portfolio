# Analytics Pipeline (DuckDB + FRED)

A small, idempotent ELT pipeline that pulls macroeconomic indicators from the
[Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) service
into a local [DuckDB](https://duckdb.org/) database, ready for analysis in
SQL, pandas, or the included notebook.

Currently tracks two daily series:

| Symbol       | Description                          |
|--------------|---------------------------------------|
| `DGS10`      | 10-Year Treasury Constant Maturity Rate |
| `DCOILWTICO` | WTI Crude Oil Price                   |

## Why this exists

FRED publishes a huge range of clean, public macro data, but it's scattered
across individual CSV endpoints and needs cleaning (missing values on
holidays/weekends, mismatched date ranges) before it's analysis-ready. This
project automates that: extract raw series -> clean & align in pandas ->
upsert into a queryable analytical table, no API key required.

## How it works

```
FRED CSV endpoints  --->  pandas (clean, align, forward-fill)  --->  DuckDB (upsert)
```

1. **Extract** (`src/ingestion.py::extract_fred_data`) — downloads each
   series directly from FRED's public `fredgraph.csv` endpoint and merges
   them into a single dataframe on date.
2. **Transform** (`src/ingestion.py::transform_and_load`) — coerces values to
   numeric, sorts by date, forward-fills gaps (e.g. weekends/holidays when
   markets are closed), and restricts the result to `2023-01-01` onward.
3. **Load** — upserts into `fact_macro_metrics` via DuckDB's
   `INSERT OR REPLACE`, keyed on `metric_date`, so re-running the pipeline is
   always safe (no duplicate or stale rows).

## Data model

`fact_macro_metrics` (`data/macro_analytics.duckdb`):

| Column       | Type      | Notes                        |
|--------------|-----------|-------------------------------|
| `metric_date`| `DATE`    | Primary key                   |
| `yield_10y`  | `DOUBLE`  | From `DGS10`                  |
| `oil_wti`    | `DOUBLE`  | From `DCOILWTICO`             |
| `updated_at` | `TIMESTAMP` | Set automatically on insert |

Schema DDL lives in `src/database.py::init_db`.

## Project structure

```
main.py                                # orchestrates the pipeline
src/
  database.py                          # DuckDB connection + schema DDL
  ingestion.py                         # extract / transform / load
tests/
  conftest.py                          # isolates tests from the real .duckdb file
  test_ingestion.py                    # cleaning, filtering, idempotency
notebooks/
  01_eda_and_exploration.ipynb         # exploratory analysis against the DuckDB file
data/
  macro_analytics.duckdb               # pipeline output (checked in for convenience)
```

## Setup & usage

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14+ (pinned in
`.python-version`).

```bash
uv sync              # install dependencies
uv run main.py       # run the pipeline: init DB -> extract -> transform -> load
uv run pytest        # run the test suite
```

To explore the data interactively, open `notebooks/01_eda_and_exploration.ipynb`
(the `dev` dependency group installs the Jupyter kernel).

## Adding a new indicator

The fact table has one fixed column per indicator, so wiring in a new FRED
series takes three small edits:

1. Add its series ID to `SYMBOLS` in `main.py`.
2. Add a column for it to `fact_macro_metrics` in `src/database.py`.
3. Map the new column in `transform_and_load` (`src/ingestion.py`).

## Design notes

- **No API key**: FRED's `fredgraph.csv` endpoint is public, so the pipeline
  has zero credentials to manage — a deliberate tradeoff for a small,
  self-contained demo over using the authenticated FRED API.
- **Idempotent by construction**: `INSERT OR REPLACE` on a primary key means
  the pipeline can be re-run any number of times (e.g. on a schedule) without
  producing duplicates or requiring manual cleanup.
- **DuckDB over Postgres/SQLite**: single-file, zero-server analytical
  database that's fast for the columnar aggregations this kind of time-series
  data is typically queried with.
