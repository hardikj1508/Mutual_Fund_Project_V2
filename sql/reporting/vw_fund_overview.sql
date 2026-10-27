
CREATE OR REPLACE VIEW reporting.vw_fund_overview AS
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    f.plan,
    f.risk_category,
    f.expense_ratio_pct,
    f.benchmark,
    sp.return_1yr_pct,
    sp.return_3yr_pct,
    sp.return_5yr_pct,
    sp.benchmark_3yr_pct,
    sp.alpha,
    sp.beta,
    sp.sharpe_ratio,
    sp.sortino_ratio,
    sp.std_dev_ann_pct,
    sp.max_drawdown_pct,
    sp.aum_crore AS scheme_aum_crore,
    sp.morningstar_rating,
    sp.risk_grade,
    a.aum_crore AS fund_house_aum_crore,
    a.date AS fund_house_aum_date
FROM analytics.fund_master AS f
LEFT JOIN analytics.scheme_performance AS sp
    ON f.amfi_code = sp.amfi_code
LEFT JOIN (
    SELECT DISTINCT ON (fund_house)
        fund_house,
        aum_crore,
        date
    FROM analytics.aum_by_fund_house
    ORDER BY fund_house, date DESC
) AS a
    ON f.fund_house = a.fund_house;
