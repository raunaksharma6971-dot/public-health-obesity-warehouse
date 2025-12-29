import duckdb

CSV_PATH = "data/raw/cdc_obesity_brfss.csv"
DB_PATH = "warehouse/analytics.duckdb"

con = duckdb.connect(DB_PATH)

# Create raw schema
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

# Drop table if it already exists
con.execute("DROP TABLE IF EXISTS raw.cdc_obesity_brfss;")

# Load CSV into DuckDB
con.execute(f"""
CREATE TABLE raw.cdc_obesity_brfss AS
SELECT *
FROM read_csv_auto('{CSV_PATH}', ignore_errors=true);
""")

# Verify load
result = con.execute(
    "SELECT COUNT(*) AS row_count FROM raw.cdc_obesity_brfss"
).fetchdf()

print(result)

con.close()
