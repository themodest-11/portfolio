# Bank Loan Portfolio Analysis — GitHub Portfolio Project

A self-contained SQL + Python + Excel project built on the Kaggle
["Bank Loan Analysis Project"](https://www.kaggle.com/datasets/sanjanamurthy392/bank-loan-analysis-project)
dataset, structured specifically to demonstrate the four points banks
ask for in a Data/Credit Analyst job description:

| # | Requirement (from the vacancy) | Where it's demonstrated |
|---|---|---|
| 1 | **Управленческая отчётность** — monthly issued/received, dynamics, plan vs fact | [`sql/02_management_reporting.sql`](sql/02_management_reporting.sql) |
| 2 | **Рентабельность сегментов** — profitability by loan type/term/region (ABC-style) | [`sql/03_profitability_by_segment.sql`](sql/03_profitability_by_segment.sql) |
| 3 | **Модель со сценариями в Excel** — profit sensitivity to rate/volume/default rate | [`excel/scenario_model.xlsx`](excel/scenario_model.xlsx) |
| 4 | **Автоматизация** — pipeline via SQL/Python instead of manual Excel | [`python/etl_pipeline.py`](python/etl_pipeline.py) |

## About the data

`data/financial_loan.csv` is the **real** dataset — 39,717 loans,
extracted from the `Merge` sheet of the original Kaggle workbook
(`python/extract_real_data.py`, run once against the downloaded
`.xlsx`) and cleaned to the column names used throughout `sql/` and
`python/`. All numbers in `reports/bank_loan_reports.xlsx` and the
`Assumptions` sheet of `excel/scenario_model.xlsx` are computed from
this real data, not a synthetic stand-in.

`data/sample_loans.csv` is a small **synthetic** 1,200-row fallback
(`python/generate_sample_data.py`, fixed random seed) kept only so the
pipeline still runs end-to-end if `financial_loan.csv` is ever removed
— `etl_pipeline.py` always prefers the real file when both exist.

**Note:** the uploaded `Bank_Loan_Analysis_Project.xlsx` workbook
itself is someone else's *finished* project (dashboards, pivot
tables, KPI sheets already built) — it isn't meant to be submitted
as-is. This repo only reuses its underlying raw records, then builds
the reporting/profitability/automation layer independently.

## Project structure

```
bank-loan-portfolio/
├── data/
│   ├── sample_loans.csv          synthetic fallback data (generated)
│   └── financial_loan.csv        real data, 39,717 loans (extracted)
├── sql/
│   ├── 01_schema_and_load.sql    table schema
│   ├── 02_management_reporting.sql   monthly issued/received, plan vs fact
│   └── 03_profitability_by_segment.sql  ABC-style profitability by segment
├── python/
│   ├── extract_real_data.py      pulls the real records out of the source .xlsx
│   ├── generate_sample_data.py   builds the synthetic fallback CSV
│   └── etl_pipeline.py           loads CSV -> SQLite, runs the SQL, exports Excel
├── excel/
│   ├── build_scenario_model.py   builds the workbook below (openpyxl, formulas only)
│   └── scenario_model.xlsx       rate/volume/default-rate sensitivity model
└── reports/
    └── bank_loan_reports.xlsx    output of the automated pipeline (generated)
```

## How to run it

```bash
pip install pandas openpyxl
python python/etl_pipeline.py           # loads data/financial_loan.csv, runs SQL, writes reports/bank_loan_reports.xlsx
```

`data/financial_loan.csv` is already included, so this runs
end-to-end immediately. If you ever need to regenerate it from the
original workbook: `python python/extract_real_data.py`.

This produces `reports/bank_loan_reports.xlsx` with three sheets:
monthly plan-vs-fact, profitability by purpose/grade, profitability by
term/region — the same numbers a monthly manual Excel exercise would
produce, generated in seconds instead of hours.

## 1. Management reporting (plan vs fact)

`sql/02_management_reporting.sql` aggregates issued volume and
received payments by month, computes month-over-month growth with a
window function (`LAG`), and compares actual issued volume to a
monthly plan target (`loan_plan` table — demo targets are `fact * 1.05`;
replace with the bank's real targets).

## 2. Segment profitability

`sql/03_profitability_by_segment.sql` computes realized profit
(`total_payment - loan_amount`) and default rate per segment
(purpose × grade, and separately term × region), then ranks segments
into an **A/B/C** classification by cumulative contribution to total
profit — the same ABC logic used for the GT Ecom store portfolio,
applied here to loan segments instead of SKUs.

## 3. Excel scenario model

`excel/scenario_model.xlsx` — all cells are live formulas (verified
with zero recalculation errors), not hardcoded numbers:

- **`Assumptions`** — baseline portfolio numbers (yellow = editable
  inputs), pulled from the SQL reporting above
- **`Scenarios`** — Base / Optimistic / Pessimistic side-by-side, each
  driven by three levers: volume change, rate change (pp), default
  rate change (pp)
- **`Sensitivity_Grid`** — a 5×5 net-profit grid across volume change
  (rows) and rate change (columns), with the default-rate stress held
  in one editable cell

## 4. Automation

`python/etl_pipeline.py` replaces the "load CSV, drag formulas, copy
into a new tab" monthly routine: it loads the raw export into SQLite,
runs the same SQL used for reporting/profitability, and writes a
ready-to-share Excel workbook — a small, honest example of "if there's
time, automate it instead of doing it by hand in Excel."

## Notes / assumptions to call out at interview

- **LGD (60%), cost of funds (5%), opex ratio (2%)** in the scenario
  model are placeholder assumptions — swap in the bank's real figures
  before using this for actual decisions (flagged in yellow with a
  note column in the `Assumptions` sheet).
- **The Base scenario currently shows a negative net profit.** With
  the real portfolio's default rate (14.17%) and the placeholder LGD
  (60%), expected credit loss (`volume × default rate × LGD`) comes
  out larger than revenue. This is a modeling limitation, not a data
  error: the model treats every defaulted dollar as a 60% loss, but
  in reality `total_payment` already includes partial recoveries
  collected before a loan is charged off, so the loss is double
  counted to some degree. Worth raising proactively in an interview —
  either lower the LGD assumption to something recoveries-adjusted,
  or rebuild expected loss from `loan_amount - total_payment` on
  charged-off loans specifically, rather than a flat rate × LGD.
- "Received" in the monthly report uses cumulative `total_payment`
  attributed to the loan's issue month (the dataset has one payment
  snapshot per loan, `last_payment_date`/`last_payment_amount`, not a
  full monthly ledger) — call this out as a known simplification.
