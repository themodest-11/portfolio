-- ============================================================
-- Schema for the Bank Loan Analysis dataset
-- Source: https://www.kaggle.com/datasets/sanjanamurthy392/bank-loan-analysis-project
-- data/financial_loan.csv is extracted from the 'Merge' sheet of the
-- workbook (python/extract_real_data.py) — column names below match
-- that export; python/etl_pipeline.py loads whichever CSV is present
-- in data/ into this table.
-- ============================================================

drop table if exists loans;

create table loans (
    id                     integer primary key,
    member_id              integer,
    issue_date             date,
    loan_amount            numeric,
    term                   text,        -- ' 36 months' / ' 60 months'
    int_rate               numeric,     -- stored as fraction, e.g. 0.1123
    installment            numeric,
    grade                  text,        -- A..G
    sub_grade              text,
    emp_length             text,
    home_ownership         text,
    annual_income          numeric,
    verification_status    text,
    loan_status            text,        -- Fully Paid / Current / Charged Off
    purpose                text,
    address_state          text,
    dti                    numeric,
    total_acc              integer,
    total_payment          numeric,     -- cumulative payments received to date
    last_payment_date      date,        -- real payment-ledger field (not in the synthetic demo)
    last_payment_amount    numeric
);
