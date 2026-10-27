
from getpass import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


DATABASE_NAME = "bluestock_mf_v2"
DATABASE_USER = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

EXPECTED_ROWS = {
    "fund_master": 40,
    "nav_history": 46000,
    "aum_by_fund_house": 90,
    "monthly_sip_inflows": 48,
    "category_inflows": 144,
    "industry_folio_count": 21,
    "scheme_performance": 40,
    "investor_transactions": 32778,
    "portfolio_holdings": 322,
    "benchmark_indices": 8050,
}


def create_database_engine():
    password = getpass("PostgreSQL password: ")

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=DATABASE_USER,
        password=password,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
    )

    return create_engine(connection_url)


# All statements run in one transaction.
# A failure rolls back the drops, table creation, inserts and constraints.
TRANSFORM_SQL = [
    # ---------------------------------------------------------
    # 1. FUND MASTER
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.fund_master (
        amfi_code INTEGER NOT NULL,
        fund_house TEXT NOT NULL,
        scheme_name TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        plan TEXT NOT NULL,
        launch_date DATE,
        benchmark TEXT,
        expense_ratio_pct NUMERIC(8,4),
        exit_load_pct NUMERIC(8,4),
        min_sip_amount NUMERIC(12,2),
        min_lumpsum_amount NUMERIC(12,2),
        fund_manager TEXT,
        risk_category TEXT,
        sebi_category_code TEXT,
        CONSTRAINT pk_fund_master PRIMARY KEY (amfi_code)
    )
    """,
    """
    INSERT INTO analytics.fund_master
    SELECT
        NULLIF(TRIM(amfi_code), '')::INTEGER,
        NULLIF(TRIM(fund_house), ''),
        NULLIF(TRIM(scheme_name), ''),
        NULLIF(TRIM(category), ''),
        NULLIF(TRIM(sub_category), ''),
        NULLIF(TRIM(plan), ''),
        NULLIF(TRIM(launch_date), '')::DATE,
        NULLIF(TRIM(benchmark), ''),
        NULLIF(TRIM(expense_ratio_pct), '')::NUMERIC(8,4),
        NULLIF(TRIM(exit_load_pct), '')::NUMERIC(8,4),
        NULLIF(TRIM(min_sip_amount), '')::NUMERIC(12,2),
        NULLIF(TRIM(min_lumpsum_amount), '')::NUMERIC(12,2),
        NULLIF(TRIM(fund_manager), ''),
        NULLIF(TRIM(risk_category), ''),
        NULLIF(TRIM(sebi_category_code), '')
    FROM staging.fund_master
    """,

    # ---------------------------------------------------------
    # 2. NAV HISTORY
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.nav_history (
        amfi_code INTEGER NOT NULL,
        date DATE NOT NULL,
        nav NUMERIC(12,4) NOT NULL,
        CONSTRAINT pk_nav_history PRIMARY KEY (amfi_code, date),
        CONSTRAINT fk_nav_history_fund_master
            FOREIGN KEY (amfi_code)
            REFERENCES analytics.fund_master(amfi_code),
        CONSTRAINT chk_nav_positive CHECK (nav > 0)
    )
    """,
    """
    INSERT INTO analytics.nav_history
    SELECT
        TRIM(amfi_code)::INTEGER,
        TRIM(date)::DATE,
        TRIM(nav)::NUMERIC(12,4)
    FROM staging.nav_history
    """,

    # ---------------------------------------------------------
    # 3. AUM BY FUND HOUSE
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.aum_by_fund_house (
        date DATE NOT NULL,
        fund_house TEXT NOT NULL,
        aum_lakh_crore NUMERIC(12,4) NOT NULL,
        aum_crore NUMERIC(14,2) NOT NULL,
        num_schemes INTEGER NOT NULL,
        CONSTRAINT pk_aum_by_fund_house
            PRIMARY KEY (date, fund_house)
    )
    """,
    """
    INSERT INTO analytics.aum_by_fund_house
    SELECT
        TRIM(date)::DATE,
        NULLIF(TRIM(fund_house), ''),
        TRIM(aum_lakh_crore)::NUMERIC(12,4),
        TRIM(aum_crore)::NUMERIC(14,2),
        TRIM(num_schemes)::INTEGER
    FROM staging.aum_by_fund_house
    """,

    # ---------------------------------------------------------
    # 4. MONTHLY SIP INFLOWS
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.monthly_sip_inflows (
        month DATE NOT NULL,
        sip_inflow_crore NUMERIC(12,2) NOT NULL,
        active_sip_accounts_crore NUMERIC(12,4) NOT NULL,
        new_sip_accounts_lakh NUMERIC(12,4) NOT NULL,
        sip_aum_lakh_crore NUMERIC(12,4) NOT NULL,
        yoy_growth_pct NUMERIC(10,4),
        CONSTRAINT pk_monthly_sip_inflows PRIMARY KEY (month)
    )
    """,
    """
    INSERT INTO analytics.monthly_sip_inflows
    SELECT
        TO_DATE(TRIM(month) || '-01', 'YYYY-MM-DD'),
        TRIM(sip_inflow_crore)::NUMERIC(12,2),
        TRIM(active_sip_accounts_crore)::NUMERIC(12,4),
        TRIM(new_sip_accounts_lakh)::NUMERIC(12,4),
        TRIM(sip_aum_lakh_crore)::NUMERIC(12,4),
        NULLIF(TRIM(yoy_growth_pct), '')::NUMERIC(10,4)
    FROM staging.monthly_sip_inflows
    """,

    # ---------------------------------------------------------
    # 5. CATEGORY INFLOWS
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.category_inflows (
        month DATE NOT NULL,
        category TEXT NOT NULL,
        net_inflow_crore NUMERIC(12,2) NOT NULL,
        CONSTRAINT pk_category_inflows
            PRIMARY KEY (month, category)
    )
    """,
    """
    INSERT INTO analytics.category_inflows
    SELECT
        TO_DATE(TRIM(month) || '-01', 'YYYY-MM-DD'),
        NULLIF(TRIM(category), ''),
        TRIM(net_inflow_crore)::NUMERIC(12,2)
    FROM staging.category_inflows
    """,

    # ---------------------------------------------------------
    # 6. INDUSTRY FOLIO COUNT
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.industry_folio_count (
        month DATE NOT NULL,
        total_folios_crore NUMERIC(12,4) NOT NULL,
        equity_folios_crore NUMERIC(12,4) NOT NULL,
        debt_folios_crore NUMERIC(12,4) NOT NULL,
        hybrid_folios_crore NUMERIC(12,4) NOT NULL,
        others_folios_crore NUMERIC(12,4) NOT NULL,
        CONSTRAINT pk_industry_folio_count PRIMARY KEY (month)
    )
    """,
    """
    INSERT INTO analytics.industry_folio_count
    SELECT
        TO_DATE(TRIM(month) || '-01', 'YYYY-MM-DD'),
        TRIM(total_folios_crore)::NUMERIC(12,4),
        TRIM(equity_folios_crore)::NUMERIC(12,4),
        TRIM(debt_folios_crore)::NUMERIC(12,4),
        TRIM(hybrid_folios_crore)::NUMERIC(12,4),
        TRIM(others_folios_crore)::NUMERIC(12,4)
    FROM staging.industry_folio_count
    """,

    # ---------------------------------------------------------
    # 7. SCHEME PERFORMANCE
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.scheme_performance (
        amfi_code INTEGER NOT NULL,
        scheme_name TEXT NOT NULL,
        fund_house TEXT NOT NULL,
        category TEXT NOT NULL,
        plan TEXT NOT NULL,
        return_1yr_pct NUMERIC(10,4) NOT NULL,
        return_3yr_pct NUMERIC(10,4) NOT NULL,
        return_5yr_pct NUMERIC(10,4) NOT NULL,
        benchmark_3yr_pct NUMERIC(10,4) NOT NULL,
        alpha NUMERIC(10,4) NOT NULL,
        beta NUMERIC(10,4) NOT NULL,
        sharpe_ratio NUMERIC(10,4) NOT NULL,
        sortino_ratio NUMERIC(10,4) NOT NULL,
        std_dev_ann_pct NUMERIC(10,4) NOT NULL,
        max_drawdown_pct NUMERIC(10,4) NOT NULL,
        aum_crore NUMERIC(14,2) NOT NULL,
        expense_ratio_pct NUMERIC(10,4) NOT NULL,
        morningstar_rating INTEGER NOT NULL,
        risk_grade TEXT NOT NULL,
        CONSTRAINT pk_scheme_performance PRIMARY KEY (amfi_code),
        CONSTRAINT fk_scheme_performance_fund_master
            FOREIGN KEY (amfi_code)
            REFERENCES analytics.fund_master(amfi_code)
    )
    """,
    """
    INSERT INTO analytics.scheme_performance
    SELECT
        TRIM(amfi_code)::INTEGER,
        NULLIF(TRIM(scheme_name), ''),
        NULLIF(TRIM(fund_house), ''),
        NULLIF(TRIM(category), ''),
        NULLIF(TRIM(plan), ''),
        TRIM(return_1yr_pct)::NUMERIC(10,4),
        TRIM(return_3yr_pct)::NUMERIC(10,4),
        TRIM(return_5yr_pct)::NUMERIC(10,4),
        TRIM(benchmark_3yr_pct)::NUMERIC(10,4),
        TRIM(alpha)::NUMERIC(10,4),
        TRIM(beta)::NUMERIC(10,4),
        TRIM(sharpe_ratio)::NUMERIC(10,4),
        TRIM(sortino_ratio)::NUMERIC(10,4),
        TRIM(std_dev_ann_pct)::NUMERIC(10,4),
        TRIM(max_drawdown_pct)::NUMERIC(10,4),
        TRIM(aum_crore)::NUMERIC(14,2),
        TRIM(expense_ratio_pct)::NUMERIC(10,4),
        TRIM(morningstar_rating)::INTEGER,
        NULLIF(TRIM(risk_grade), '')
    FROM staging.scheme_performance
    """,

    # ---------------------------------------------------------
    # 8. INVESTOR TRANSACTIONS
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.investor_transactions (
        transaction_row_id BIGINT NOT NULL,
        investor_id TEXT NOT NULL,
        transaction_date DATE NOT NULL,
        amfi_code INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        amount_inr NUMERIC(14,2) NOT NULL,
        state TEXT NOT NULL,
        city TEXT NOT NULL,
        city_tier TEXT NOT NULL,
        age_group TEXT NOT NULL,
        gender TEXT NOT NULL,
        annual_income_lakh NUMERIC(12,2) NOT NULL,
        payment_mode TEXT NOT NULL,
        kyc_status TEXT NOT NULL,
        CONSTRAINT pk_investor_transactions
            PRIMARY KEY (transaction_row_id),
        CONSTRAINT fk_investor_transactions_fund_master
            FOREIGN KEY (amfi_code)
            REFERENCES analytics.fund_master(amfi_code)
    )
    """,
    """
    INSERT INTO analytics.investor_transactions
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY
                TRIM(transaction_date),
                TRIM(investor_id),
                TRIM(amfi_code),
                TRIM(transaction_type),
                TRIM(amount_inr),
                TRIM(state),
                TRIM(city),
                TRIM(city_tier),
                TRIM(age_group),
                TRIM(gender),
                TRIM(annual_income_lakh),
                TRIM(payment_mode),
                TRIM(kyc_status)
        )::BIGINT,
        NULLIF(TRIM(investor_id), ''),
        TRIM(transaction_date)::DATE,
        TRIM(amfi_code)::INTEGER,
        NULLIF(TRIM(transaction_type), ''),
        TRIM(amount_inr)::NUMERIC(14,2),
        NULLIF(TRIM(state), ''),
        NULLIF(TRIM(city), ''),
        NULLIF(TRIM(city_tier), ''),
        NULLIF(TRIM(age_group), ''),
        NULLIF(TRIM(gender), ''),
        TRIM(annual_income_lakh)::NUMERIC(12,2),
        NULLIF(TRIM(payment_mode), ''),
        NULLIF(TRIM(kyc_status), '')
    FROM staging.investor_transactions
    """,

    # ---------------------------------------------------------
    # 9. PORTFOLIO HOLDINGS
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.portfolio_holdings (
        amfi_code INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        stock_name TEXT NOT NULL,
        sector TEXT NOT NULL,
        weight_pct NUMERIC(10,4) NOT NULL,
        market_value_cr NUMERIC(14,2) NOT NULL,
        current_price_inr NUMERIC(14,2) NOT NULL,
        portfolio_date DATE NOT NULL,
        CONSTRAINT pk_portfolio_holdings
            PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
        CONSTRAINT fk_portfolio_holdings_fund_master
            FOREIGN KEY (amfi_code)
            REFERENCES analytics.fund_master(amfi_code)
    )
    """,
    """
    INSERT INTO analytics.portfolio_holdings
    SELECT
        TRIM(amfi_code)::INTEGER,
        NULLIF(TRIM(stock_symbol), ''),
        NULLIF(TRIM(stock_name), ''),
        NULLIF(TRIM(sector), ''),
        TRIM(weight_pct)::NUMERIC(10,4),
        TRIM(market_value_cr)::NUMERIC(14,2),
        TRIM(current_price_inr)::NUMERIC(14,2),
        TRIM(portfolio_date)::DATE
    FROM staging.portfolio_holdings
    """,

    # ---------------------------------------------------------
    # 10. BENCHMARK INDICES
    # ---------------------------------------------------------
    """
    CREATE TABLE analytics.benchmark_indices (
        date DATE NOT NULL,
        index_name TEXT NOT NULL,
        close_value NUMERIC(14,2) NOT NULL,
        CONSTRAINT pk_benchmark_indices PRIMARY KEY (date, index_name),
        CONSTRAINT chk_benchmark_indices_close_value
            CHECK (close_value > 0)
    )
    """,
    """
    INSERT INTO analytics.benchmark_indices
    SELECT
        TRIM(date)::DATE,
        NULLIF(TRIM(index_name), ''),
        TRIM(close_value)::NUMERIC(14,2)
    FROM staging.benchmark_indices
    """,
]


def rebuild_analytics(engine):
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))

        # Drop child tables before their referenced parent table.
        for table_name in [
            "investor_transactions",
            "nav_history",
            "portfolio_holdings",
            "scheme_performance",
            "benchmark_indices",
            "category_inflows",
            "monthly_sip_inflows",
            "industry_folio_count",
            "aum_by_fund_house",
            "fund_master",
        ]:
            connection.execute(
                text(f"DROP TABLE IF EXISTS analytics.{table_name} CASCADE")
            )

        for statement in TRANSFORM_SQL:
            connection.execute(text(statement))

        print("\nRow-count validation:")
        for table_name, expected_count in EXPECTED_ROWS.items():
            actual_count = connection.execute(
                text(f"SELECT COUNT(*) FROM analytics.{table_name}")
            ).scalar_one()

            print(
                f"{'PASS' if actual_count == expected_count else 'FAIL'} | "
                f"{table_name}: {actual_count:,} rows"
            )

            if actual_count != expected_count:
                raise RuntimeError(
                    f"Row-count mismatch in {table_name}: "
                    f"expected {expected_count}, got {actual_count}"
                )

        # Explicit foreign-key orphan checks.
        for table_name in [
            "nav_history",
            "scheme_performance",
            "investor_transactions",
            "portfolio_holdings",
        ]:
            orphan_count = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM analytics.{table_name} AS child
                    LEFT JOIN analytics.fund_master AS parent
                      ON child.amfi_code = parent.amfi_code
                    WHERE parent.amfi_code IS NULL
                    """
                )
            ).scalar_one()

            if orphan_count:
                raise RuntimeError(
                    f"{table_name} contains {orphan_count} orphan fund codes"
                )

            print(f"PASS | {table_name}: no orphan fund codes")

        duplicate_benchmark_keys = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT date, index_name
                    FROM analytics.benchmark_indices
                    GROUP BY date, index_name
                    HAVING COUNT(*) > 1
                ) AS duplicates
                """
            )
        ).scalar_one()

        if duplicate_benchmark_keys:
            raise RuntimeError("Duplicate benchmark date/index keys found")

        print("PASS | benchmark date/index keys are unique")

    # engine.begin() commits only if all statements and checks succeed.
    print("\nAnalytics rebuild committed successfully.")


if __name__ == "__main__":
    engine = create_database_engine()

    try:
        rebuild_analytics(engine)
    except Exception:
        print(
            "\nREBUILD FAILED. The analytics transaction was rolled back. "
            "Review the error above before trying again."
        )
        raise
    finally:
        engine.dispose()
