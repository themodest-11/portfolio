"""
Requirement 4: Automation.
Loads the raw loan export into SQLite, runs the management-reporting and
segment-profitability SQL (sql/02, sql/03), and writes the results to a
single Excel workbook — one sheet per report — instead of doing this by
hand in Excel every month.

Usage:
    python etl_pipeline.py

Looks for data/financial_loan.csv first (the real Kaggle export);
falls back to data/sample_loans.csv (synthetic demo data) if that file
isn't present yet.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SQL_DIR = ROOT / "sql"
DB_PATH = ROOT / "loans.db"
OUT_PATH = ROOT / "reports" / "bank_loan_reports.xlsx"


def pick_source_csv() -> Path:
    real = DATA_DIR / "financial_loan.csv"
    sample = DATA_DIR / "sample_loans.csv"
    if real.exists():
        print(f"Using real dataset: {real.name}")
        return real
    if sample.exists():
        print(f"Real dataset not found — using synthetic demo data: {sample.name}")
        return sample
    sys.exit("No CSV found in data/. Run generate_sample_data.py or add financial_loan.csv.")


def load_to_sqlite(csv_path: Path, conn: sqlite3.Connection) -> None:
    schema_sql = (SQL_DIR / "01_schema_and_load.sql").read_text()
    conn.executescript(schema_sql)

    df = pd.read_csv(csv_path)
    df.to_sql("loans", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into loans")


def run_report(sql_path: Path, conn: sqlite3.Connection) -> dict:
    """Splits a .sql file on ';' and runs each statement; returns the
    last SELECT's result as a DataFrame keyed by a label per statement
    block found in the file (comment lines starting with '--' before a
    SELECT are used as sheet-ish context, kept simple here: we just run
    every statement and collect any that return rows)."""
    raw = sql_path.read_text()
    statements = [s.strip() for s in raw.split(";") if s.strip()]
    results = []
    for stmt in statements:
        cur = conn.execute(stmt)
        if cur.description:  # SELECT-type statement, has rows to fetch
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
            results.append(pd.DataFrame(rows, columns=cols))
    return results


def main():
    DATA_DIR.mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)

    csv_path = pick_source_csv()

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)

    load_to_sqlite(csv_path, conn)

    management_reports = run_report(SQL_DIR / "02_management_reporting.sql", conn)
    profitability_reports = run_report(SQL_DIR / "03_profitability_by_segment.sql", conn)

    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as writer:
        # 02_management_reporting.sql's final SELECT is the monthly report
        management_reports[-1].to_excel(writer, sheet_name="Monthly_Plan_vs_Fact", index=False)

        # 03_profitability_by_segment.sql has two SELECTs: purpose/grade, then term/region
        profitability_reports[0].to_excel(writer, sheet_name="Profitability_Purpose_Grade", index=False)
        profitability_reports[1].to_excel(writer, sheet_name="Profitability_Term_Region", index=False)

    conn.close()
    print(f"Reports written to {OUT_PATH}")


if __name__ == "__main__":
    main()
