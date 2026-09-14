"""
Generates a small SYNTHETIC sample (data/sample_loans.csv) that mirrors the
column structure of the Kaggle "Bank Loan Analysis Project" dataset:
https://www.kaggle.com/datasets/sanjanamurthy392/bank-loan-analysis-project

This is only a stand-in so the pipeline in this repo runs end-to-end without
the real file. Replace data/financial_loan.csv with the actual Kaggle export
and the SQL/Python scripts will work unchanged (same column names).
"""

import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)

N = 1200
STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "WA"]
PURPOSES = ["debt_consolidation", "credit_card", "home_improvement",
            "small_business", "major_purchase", "car", "medical"]
GRADES = ["A", "B", "C", "D", "E", "F", "G"]
GRADE_RATE = {"A": 0.07, "B": 0.09, "C": 0.11, "D": 0.14,
              "E": 0.17, "F": 0.20, "G": 0.24}
TERMS = [" 36 months", " 60 months"]
HOME = ["RENT", "OWN", "MORTGAGE"]
VERIF = ["Verified", "Source Verified", "Not Verified"]
STATUS = ["Fully Paid", "Current", "Charged Off"]
STATUS_W = [0.55, 0.32, 0.13]

start = date(2021, 1, 1)

rows = []
for i in range(1, N + 1):
    issue = start + timedelta(days=random.randint(0, 1095))
    grade = random.choice(GRADES)
    term = random.choice(TERMS)
    term_months = 36 if "36" in term else 60
    loan_amount = random.randint(2, 40) * 1000
    int_rate = round(GRADE_RATE[grade] + random.uniform(-0.01, 0.02), 4)
    installment = round(loan_amount * (int_rate / 12) /
                         (1 - (1 + int_rate / 12) ** (-term_months)), 2)
    status = random.choices(STATUS, weights=STATUS_W, k=1)[0]
    total_payment = round(installment * random.randint(1, term_months)
                           if status != "Fully Paid" else installment * term_months, 2)
    annual_income = random.randint(28, 180) * 1000
    dti = round(random.uniform(3, 35), 2)

    rows.append({
        "id": i,
        "member_id": 100000 + i,
        "issue_date": issue.isoformat(),
        "loan_amount": loan_amount,
        "term": term,
        "int_rate": int_rate,
        "installment": installment,
        "grade": grade,
        "sub_grade": grade + str(random.randint(1, 5)),
        "emp_length": random.choice(["< 1 year", "1 year", "3 years", "5 years",
                                      "10+ years", "2 years"]),
        "home_ownership": random.choice(HOME),
        "annual_income": annual_income,
        "verification_status": random.choice(VERIF),
        "loan_status": status,
        "purpose": random.choice(PURPOSES),
        "address_state": random.choice(STATES),
        "dti": dti,
        "total_acc": random.randint(5, 40),
        "total_payment": total_payment,
        "application_type": "INDIVIDUAL",
    })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/bank-loan-portfolio/data/sample_loans.csv", index=False)
print(f"Wrote {len(df)} rows")
