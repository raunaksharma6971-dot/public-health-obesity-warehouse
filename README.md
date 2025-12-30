# public-health-obesity-warehouse
python - << 'PY'
import duckdb
con = duckdb.connect("warehouse/analytics.duckdb")

print("\nTop 10 obesity states (latest year):")
print(con.execute("""
SELECT * FROM marts.mart_obesity_latest_rank LIMIT 10;
""").fetchdf())

print("\nBottom 10 obesity states (latest year):")
print(con.execute("""
SELECT * FROM marts.mart_obesity_latest_rank
ORDER BY obesity_rank_high_to_low DESC
LIMIT 10;
""").fetchdf())

print("\nStates with largest obesity increase from 2011 to 2024 (where available):")
print(con.execute("""
WITH start_year AS (SELECT 2011 AS y),
     end_year AS (SELECT 2024 AS y),
s AS (
  SELECT state, obesity_pct AS obesity_2011
  FROM marts.mart_obesity_trends
  WHERE year = 2011
),
e AS (
  SELECT state, obesity_pct AS obesity_2024
  FROM marts.mart_obesity_trends
  WHERE year = 2024
)
SELECT
  e.state,
  s.obesity_2011,
  e.obesity_2024,
  (e.obesity_2024 - s.obesity_2011) AS change_2011_to_2024
FROM e
JOIN s USING (state)
ORDER BY change_2011_to_2024 DESC
LIMIT 10;
""").fetchdf())

con.close()
PY



## Health Disparities Insights (Stratified Analysis)

To evaluate equity gaps, the pipeline builds stratified marts for adult obesity prevalence by:
- Income
- Education
- Sex
- Race/Ethnicity

These marts enable comparisons across groups over time and geography.

### Obesity % by Income Group (Latest Year)
![Obesity by Income](dashboards/obesity_by_income_latest.png)

### Obesity % by Education Level (Latest Year)
![Obesity by Education](dashboards/obesity_by_education_latest.png)

**Marts used**
- `marts.mart_obesity_by_income`
- `marts.mart_obesity_by_education`
- `marts.mart_obesity_by_sex`
- `marts.mart_obesity_by_race`
