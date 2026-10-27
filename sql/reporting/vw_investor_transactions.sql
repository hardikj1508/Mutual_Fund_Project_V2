
CREATE OR REPLACE VIEW reporting.vw_investor_transactions AS
SELECT
    t.transaction_row_id,
    t.investor_id,
    t.transaction_date,
    t.transaction_type,
    t.amount_inr,
    t.state,
    t.city,
    t.city_tier,
    t.age_group,
    t.gender,
    t.annual_income_lakh,
    t.payment_mode,
    t.kyc_status,
    t.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    f.plan,
    f.risk_category
FROM analytics.investor_transactions AS t
LEFT JOIN analytics.fund_master AS f
    ON t.amfi_code = f.amfi_code;
