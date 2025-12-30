import duckdb

DB_PATH = "warehouse/analytics.duckdb"
con = duckdb.connect(DB_PATH)

print("Starting disparity marts build...")

OBESITY_QUESTION = "Percent of adults aged 18 years and older who have obesity"

# Base stratified view (exclude Total population)
con.execute("""
CREATE OR REPLACE VIEW marts.v_base_stratified AS
SELECT
    CAST(YearStart AS INTEGER) AS year,
    LocationAbbr AS state,
    Question AS question,
    CAST(Data_Value AS DOUBLE) AS value,
    StratificationCategory1 AS strat_category,
    Stratification1 AS strat_value
FROM raw.cdc_obesity_brfss
WHERE Data_Value IS NOT NULL
  AND LocationAbbr IS NOT NULL
  AND YearStart IS NOT NULL
  AND Total IS NULL;
""")

# Income disparity
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_by_income AS
SELECT
    year,
    state,
    strat_value AS income_group,
    AVG(value) AS obesity_pct
FROM marts.v_base_stratified
WHERE question = ?
  AND strat_category = 'Income'
  AND value BETWEEN 0 AND 100
GROUP BY year, state, income_group;
""", [OBESITY_QUESTION])

# Education disparity
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_by_education AS
SELECT
    year,
    state,
    strat_value AS education_level,
    AVG(value) AS obesity_pct
FROM marts.v_base_stratified
WHERE question = ?
  AND strat_category = 'Education'
  AND value BETWEEN 0 AND 100
GROUP BY year, state, education_level;
""", [OBESITY_QUESTION])

# Sex disparity
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_by_sex AS
SELECT
    year,
    state,
    strat_value AS sex,
    AVG(value) AS obesity_pct
FROM marts.v_base_stratified
WHERE question = ?
  AND strat_category = 'Sex'
  AND value BETWEEN 0 AND 100
GROUP BY year, state, sex;
""", [OBESITY_QUESTION])

# Race / Ethnicity disparity
con.execute("""
CREATE OR REPLACE TABLE marts.mart_obesity_by_race AS
SELECT
    year,
    state,
    strat_value AS race_ethnicity,
    AVG(value) AS obesity_pct
FROM marts.v_base_stratified
WHERE question = ?
  AND strat_category = 'Race/Ethnicity'
  AND value BETWEEN 0 AND 100
GROUP BY year, state, race_ethnicity;
""", [OBESITY_QUESTION])

print("✅ Disparity marts created:")
print(
    con.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='marts'
      AND table_name LIKE 'mart_obesity_by_%'
    ORDER BY table_name;
    """).fetchdf()
)

con.close()
print("Done.")
