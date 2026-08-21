"""Entry point for the FRED -> DuckDB analytics pipeline."""
import logging

from src.database import init_db
from src.ingestion import extract_fred_data, transform_and_load

# Tied 1:1 to the fact_macro_metrics schema (yield_10y, oil_wti) and the
# column mapping in transform_and_load — see README/CLAUDE.md for how to add one.
SYMBOLS = ["DGS10", "DCOILWTICO"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing DuckDB database and schemas...")
    init_db()

    logger.info("Extracting indicators from FRED: %s", SYMBOLS)
    raw_data = extract_fred_data(SYMBOLS)

    logger.info("Transforming and upserting into fact_macro_metrics...")
    transform_and_load(raw_data)

    logger.info("Pipeline executed successfully.")


if __name__ == "__main__":
    main()
