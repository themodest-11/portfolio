-- ============================================================
-- Requirement 2: Рентабельность сегментов
-- Profitability by loan type (purpose/grade), term and region (state) —
-- the credit-portfolio analog of the ABC/XYZ segmentation used on the
-- GT Ecom store portfolio.
--
-- ASSUMPTION: realized_profit = total_payment - loan_amount (received
-- minus disbursed to date). For Charged Off loans this is typically
-- negative — that is the point, it is the credit-risk signal.
-- ============================================================

with segment_base as (
    select
        purpose,
        grade,
        term,
        address_state,
        loan_status,
        loan_amount,
        total_payment,
        (total_payment - loan_amount)                     as realized_profit,
        (total_payment - loan_amount) / nullif(loan_amount, 0) as profit_margin
    from loans
),
by_purpose_grade as (
    select
        purpose,
        grade,
        count(*)                                   as loans_count,
        sum(loan_amount)                           as total_disbursed,
        sum(realized_profit)                       as total_profit,
        round(avg(profit_margin), 4)               as avg_margin,
        round(
            sum(case when loan_status = 'Charged Off' then 1.0 else 0 end)
            / count(*), 4
        )                                          as default_rate
    from segment_base
    group by purpose, grade
)
select *,
    -- ABC by contribution to total profit (A = top contributors)
    case
        when cume_dist_profit <= 0.8 then 'A'
        when cume_dist_profit <= 0.95 then 'B'
        else 'C'
    end as abc_class
from (
    select
        *,
        sum(total_profit) over (order by total_profit desc
                                 rows between unbounded preceding and current row)
        * 1.0 / sum(total_profit) over ()          as cume_dist_profit
    from by_purpose_grade
)
order by total_profit desc;

-- Same idea, sliced by term and region instead:
-- (run separately)
select
    term,
    address_state,
    count(*)                                        as loans_count,
    sum(loan_amount)                                 as total_disbursed,
    sum(total_payment - loan_amount)                 as total_profit,
    round(avg((total_payment - loan_amount) / nullif(loan_amount, 0)), 4) as avg_margin,
    round(
        sum(case when loan_status = 'Charged Off' then 1.0 else 0 end)
        / count(*), 4
    )                                                as default_rate
from loans
group by term, address_state
order by total_profit desc;
