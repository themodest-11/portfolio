"""
Extracts the real loan records from the uploaded workbook
(Bank_Loan_Analysis_Project.xlsx, sheet 'Merge' — the raw Finance1+Finance2
join before any dashboard/pivot work) and writes a clean
data/financial_loan.csv matching the column names used throughout
sql/ and python/ in this project.
"""

import pandas as pd

SRC = "/mnt/user-data/uploads/Bank_Loan_Analysis_Project.xlsx"
OUT = "/home/claude/bank-loan-portfolio/data/financial_loan.csv"

df = pd.read_excel(SRC, sheet_name="Merge")

# Drop the 'Finance2.' prefix picked up during the original merge
df.columns = [c.replace("Finance2.", "") for c in df.columns]

rename_map = {
    "loan_amnt": "loan_amount",
    "annual_inc": "annual_income",
    "issue_d": "issue_date",
    "addr_state": "address_state",
    "total_pymnt": "total_payment",
    "last_pymnt_d": "last_payment_date",
    "last_pymnt_amnt": "last_payment_amount",
    "last_credit_pull_d": "last_credit_pull_date",
}
df = df.rename(columns=rename_map)

keep_cols = [
    "id", "member_id", "issue_date", "loan_amount", "term", "int_rate",
    "installment", "grade", "sub_grade", "emp_length", "home_ownership",
    "annual_income", "verification_status", "loan_status", "purpose",
    "address_state", "dti", "total_acc", "total_payment",
    "last_payment_date", "last_payment_amount",
]
df = df[keep_cols].copy()

# int_rate in this file is already a fraction (0.1189 = 11.89%) — matches
# the schema's convention, no conversion needed.

df["issue_date"] = pd.to_datetime(df["issue_date"]).dt.date
df["last_payment_date"] = pd.to_datetime(df["last_payment_date"]).dt.date

df.to_csv(OUT, index=False)
print(f"Wrote {len(df)} rows, {len(df.columns)} columns -> {OUT}")
print(df.head(3).to_string())
