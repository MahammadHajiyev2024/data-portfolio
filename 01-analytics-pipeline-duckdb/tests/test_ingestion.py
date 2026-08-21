import pandas as pd

from src.database import get_connection
from src.ingestion import transform_and_load


def _raw_df():
    return pd.DataFrame(
        {
            "metric_date": pd.to_datetime(["2022-12-31", "2023-01-02", "2023-01-03"]),
            "DGS10": [3.5, None, 3.7],
            "DCOILWTICO": [70.0, 71.0, None],
        }
    )


def test_transform_and_load_forward_fills_and_filters_pre_2023(temp_db):
    transform_and_load(_raw_df())

    with get_connection() as con:
        result = con.execute(
            "SELECT metric_date, yield_10y, oil_wti FROM fact_macro_metrics ORDER BY metric_date"
        ).fetchdf()

    # 2022-12-31 is dropped by the 2023-01-01 cutoff.
    assert result["metric_date"].dt.strftime("%Y-%m-%d").tolist() == ["2023-01-02", "2023-01-03"]
    # Missing 2023-01-02 yield is forward-filled from the (later-filtered-out) 2022-12-31 row.
    assert result["yield_10y"].tolist() == [3.5, 3.7]
    # Missing 2023-01-03 oil price is forward-filled from 2023-01-02.
    assert result["oil_wti"].tolist() == [71.0, 71.0]


def test_transform_and_load_is_idempotent(temp_db):
    transform_and_load(_raw_df())
    transform_and_load(_raw_df())

    with get_connection() as con:
        row_count = con.execute("SELECT COUNT(*) FROM fact_macro_metrics").fetchone()[0]

    assert row_count == 2
