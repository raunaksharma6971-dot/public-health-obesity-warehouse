import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

DB_PATH = "warehouse/analytics.duckdb"
OUT_DIR = Path("dashboards")
OUT_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH)

# 1) Average obesity % over time (avg across states)
trend = con.execute("""
SELECT year, AVG(obesity_pct) AS avg_obesity_pct
FROM marts.mart_obesity_trends
GROUP BY 1
ORDER BY 1;
""").fetchdf()

plt.figure()
plt.plot(trend["year"], trend["avg_obesity_pct"])
plt.title("Average Adult Obesity % Over Time (Avg Across States)")
plt.xlabel("Year")
plt.ylabel("Obesity %")
plt.tight_layout()
plt.savefig(OUT_DIR / "avg_obesity_trend.png")
plt.close()

# 2) Top 10 states by obesity (latest year)
top10 = con.execute("""
SELECT state, obesity_pct
FROM marts.mart_obesity_latest_rank
ORDER BY obesity_rank_high_to_low
LIMIT 10;
""").fetchdf()

plt.figure()
plt.bar(top10["state"], top10["obesity_pct"])
plt.title("Top 10 States by Adult Obesity % (Latest Year)")
plt.xlabel("State")
plt.ylabel("Obesity %")
plt.tight_layout()
plt.savefig(OUT_DIR / "top10_obesity_latest.png")
plt.close()

# 3) Relationship: obesity vs no leisure-time activity (latest year)
corr = con.execute("""
WITH latest AS (
  SELECT MAX(year) AS max_year FROM marts.mart_obesity_trends
),
o AS (
  SELECT year, state, obesity_pct
  FROM marts.mart_obesity_trends
),
a AS (
  SELECT year, state, no_activity_pct
  FROM marts.mart_no_activity_trends
)
SELECT
  o.state,
  o.obesity_pct,
  a.no_activity_pct
FROM o
JOIN a USING (year, state)
JOIN latest l ON o.year = l.max_year
WHERE a.no_activity_pct IS NOT NULL;
""").fetchdf()

plt.figure()
plt.scatter(corr["no_activity_pct"], corr["obesity_pct"])
plt.title("Obesity % vs No Leisure-Time Physical Activity % (Latest Year)")
plt.xlabel("No leisure-time physical activity %")
plt.ylabel("Obesity %")
plt.tight_layout()
plt.savefig(OUT_DIR / "obesity_vs_no_activity_latest.png")
plt.close()

con.close()
print("✅ Charts saved in dashboards/:")
print("- avg_obesity_trend.png")
print("- top10_obesity_latest.png")
print("- obesity_vs_no_activity_latest.png")
