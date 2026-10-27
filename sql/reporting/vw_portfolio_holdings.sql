
CREATE OR REPLACE VIEW reporting.vw_portfolio_holdings AS
SELECT
    p.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category AS fund_category,
    p.portfolio_date,
    p.stock_symbol,
    p.stock_name,
    p.sector,
    p.weight_pct,
    p.market_value_cr,
    p.current_price_inr
FROM analytics.portfolio_holdings AS p
LEFT JOIN analytics.fund_master AS f
    ON p.amfi_code = f.amfi_code;
