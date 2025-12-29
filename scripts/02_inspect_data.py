import duckdb

DB_PATH = "warehouse/analytics.duckdb"

# Connect to DuckDB
con = duckdb.connect(DB_PATH)

print("\n=== TABLE STRUCTURE ===")
print(con.execute("DESCRIBE raw.cdc_obesity_brfss").fetchdf())

print("\n=== SAMPLE ROWS ===")
print(con.execute("SELECT * FROM raw.cdc_obesity_brfss LIMIT 5").fetchdf())

print("\n=== TOP 10 QUESTIONS / INDICATORS ===")
query_questions = """
SELECT
    Question,
    COUNT(*) AS row_count
FROM raw.cdc_obesity_brfss
GROUP BY Question
ORDER BY row_count DESC
LIMIT 10;
"""
print(con.execute(query_questions).fetchdf())

print("\n=== YEAR RANGE ===")
query_years = """
SELECT
    MIN(YearStart) AS min_year,
    MAX(YearStart) AS max_year
FROM raw.cdc_obesity_brfss;
"""
print(con.execute(query_years).fetchdf())

con.close()
