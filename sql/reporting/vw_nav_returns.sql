
CREATE OR REPLACE VIEW reporting.vw_nav_returns AS
SELECT
    amfi_code,
    date,
    nav,
    LAG(nav) OVER (
        PARTITION BY amfi_code
        ORDER BY date
    ) AS previous_nav,
    ROUND(
        (
            (
                nav / NULLIF(
                    LAG(nav) OVER (
                        PARTITION BY amfi_code
                        ORDER BY date
                    ),
                    0
                )
            ) - 1
        ) * 100,
        4
    ) AS daily_return_pct
FROM analytics.nav_history;
