-- ============================================================
-- Requirement 1: Управленческая отчётность
-- Monthly issued / received, month-over-month dynamics, plan vs fact.
--
-- ASSUMPTION (documented, since the raw dataset has no payment ledger):
-- "received" is approximated as total_payment attributed to the loan's
-- issue month (i.e. cumulative payments to date on loans issued that
-- month). Swap in a real payments table if/when available.
--
-- "plan" is a condition target set in loan_plan (self-defined, as the
-- brief allows) — replace with the bank's actual monthly targets.
-- ============================================================

-- Optional: a simple monthly plan table you can edit with real targets
drop table if exists loan_plan;
create table loan_plan (
    plan_month   text primary key,   -- 'YYYY-MM'
    plan_amount  numeric             -- target issued volume for the month
);

-- Example targets — replace with real ones
insert into loan_plan (plan_month, plan_amount)
select
    strftime('%Y-%m', issue_date) as plan_month,
    sum(loan_amount) * 1.05        as plan_amount   -- demo target = fact * 1.05
from loans
group by 1;

-- Monthly issued / received + dynamics vs prior month
with monthly as (
    select
        strftime('%Y-%m', issue_date) as report_month,
        sum(loan_amount)              as issued_amount,
        sum(total_payment)            as received_amount,
        count(*)                      as loans_count
    from loans
    group by 1
),
with_dynamics as (
    select
        report_month,
        issued_amount,
        received_amount,
        loans_count,
        lag(issued_amount) over (order by report_month) as prev_issued,
        round(
            (issued_amount - lag(issued_amount) over (order by report_month))
            * 1.0 / nullif(lag(issued_amount) over (order by report_month), 0),
            4
        ) as mom_growth
    from monthly
)
select
    d.report_month,
    d.issued_amount,
    d.received_amount,
    d.loans_count,
    d.mom_growth,
    p.plan_amount,
    round(d.issued_amount * 1.0 / nullif(p.plan_amount, 0), 4) as plan_fact_pct
from with_dynamics d
left join loan_plan p
    on p.plan_month = d.report_month
order by d.report_month;
