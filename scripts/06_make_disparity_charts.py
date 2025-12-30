import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

DB_PATH = "warehouse/analytics.duckdb"
OUT_DIR = Path("dashboards")
OUT_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH)

# Detect latest year available
latest_year = con.execute("""
SELECT MAX(year) AS y FROM marts.mart_obesity_trends;
""").fetchone()[0]

# 1) Income disparities (latest year, avg across states)
income = con.execute("""
SELECT income_group, AVG(obesity_pct) AS avg_obesity_pct
FROM marts.mart_obesity_by_income
WHERE year = ?
GROUP BY income_group
ORDER BY avg_obesity_pct DESC;
""", [latest_year]).fetchdf()

plt.figure()
plt.bar(income["income_group"], income["avg_obesity_pct"])
plt.title(f"Obesity % by Income Group (Avg Across States, {latest_year})")
plt.xlabel("Income group")
plt.ylabel("Avg obesity %")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(OUT_DIR / "obesity_by_income_latest.png")
plt.close()

# 2) Education disparities (latest year, avg across states)
edu = con.execute("""
SELECT education_level, AVG(obesity_pct) AS avg_obesity_pct
FROM marts.mart_obesity_by_education
WHERE year = ?
GROUP BY education_level
ORDER BY avg_obesity_pct DESC;
""", [latest_year]).fetchdf()

plt.figure()
plt.bar(edu["education_level"], edu["avg_obesity_pct"])
plt.title(f"Obesity % by Education Level (Avg Across States, {latest_year})")
plt.xlabel("Education level")
plt.ylabel("Avg obesity %")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(OUT_DIR / "obesity_by_education_latest.png")
plt.close()

con.close()
print("✅ Disparity charts saved in dashboards/:")
print("- obesity_by_income_latest.png")
print("- obesity_by_education_latest.png")
