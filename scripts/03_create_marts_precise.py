import duckdb

DB_PATH = "warehouse/analytics.duckdb"
con = duckdb.connect(DB_PATH)

print("Starting marts build...")

# Create marts schema
con.execute("CREATE SCHEMA IF NOT EXISTS marts;")

# Exact CDC questions
OBESITY_QUESTION = "Percent of adults aged 18 years and older who have obesity"
NO_ACTIVITY_QUESTION = "Percent of adults who engage in no leisure-time physical activity"
FRUIT_LT1_QUESTION = "Percent of adults who report consuming fruit less than one time daily"
VEG_LT1_QUESTION = "Percent of adults who report consuming vegetables less than one time daily"

# Base view (Total population only)
con.execute("""
CREATE OR REPLACE VIEW marts.v_base_total AS
SELECT
    CAST(YearStart AS INTEGER) AS year,
    LocationAbbr AS state,
    LocationDesc AS location_desc,
    Question AS question,
    CAST(Data_Value AS DOUBLE) AS value,
    Data_Value_Unit AS unit,
    Total,
    GeoLocation
FROM raw.cdc_obesity_brfss
WHERE Data_Value IS NOT NULL
  AND LocationAbbr IS NOT NULL
  AND YearStart IS NOT NULL
  AND Total = 'Total';
""")

# Obesity trends
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_trends AS
SELECT
    year,
    state,
    AVG(value) AS obesity_pct
FROM marts.v_base_total
WHERE question = ?
  AND value BETWEEN 0 AND 100
GROUP BY year, state
ORDER BY year, state;
""", [OBESITY_QUESTION])

# No activity trends
con.execute("""
CREATE OR REPLACE TABLE marts.mart_no_activity_trends AS
SELECT
    year,
    state,
    AVG(value) AS no_activity_pct
FROM marts.v_base_total
WHERE question = ?
  AND value BETWEEN 0 AND 100
GROUP BY year, state
ORDER BY year, state;
""", [NO_ACTIVITY_QUESTION])

# Fruit < 1/day
con.execute("""
CREATE OR REPLACE TABLE marts.mart_fruit_lt1_trends AS
SELECT
    year,
    state,
    AVG(value) AS fruit_lt1_pct
FROM marts.v_base_total
WHERE question = ?
  AND value BETWEEN 0 AND 100
GROUP BY year, state
ORDER BY year, state;
""", [FRUIT_LT1_QUESTION])

# Vegetables < 1/day
con.execute("""
CREATE OR REPLACE TABLE marts.mart_veg_lt1_trends AS
SELECT
    year,
    state,
    AVG(value) AS veg_lt1_pct
FROM marts.v_base_total
WHERE question = ?
  AND value BETWEEN 0 AND 100
GROUP BY year, state
ORDER BY year, state;
""", [VEG_LT1_QUESTION])

# Latest-year obesity ranking
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_latest_rank AS
WITH latest AS (
    SELECT MAX(year) AS max_year
    FROM marts.mart_obesity_trends
)
SELECT
    t.year,
    t.state,
    t.obesity_pct,
    RANK() OVER (ORDER BY t.obesity_pct DESC) AS obesity_rank_high_to_low
FROM marts.mart_obesity_trends t
JOIN latest l
  ON t.year = l.max_year
ORDER BY obesity_rank_high_to_low;
""")

print("✅ Marts created. Listing marts tables:")
print(con.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'marts'
ORDER BY table_name;
""").fetchdf())

print("\n✅ Obesity latest rank (top 10):")
print(con.execute("""
SELECT *
FROM marts.mart_obesity_latest_rank
LIMIT 10;
""").fetchdf())

print("\n✅ Year range:")
print(con.execute("""
SELECT MIN(year) AS min_year, MAX(year) AS max_year
FROM marts.mart_obesity_trends;
""").fetchdf())

con.close()
print("Done.")
