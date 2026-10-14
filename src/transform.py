from getpass import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

DATABASE_NAME = "bluestock_mf_v2"
DATABASE_USER = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

def create_database_engine():

    password = getpass("PostgreSQL password: ")

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=DATABASE_USER,
        password=password,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME
    )

    return create_engine(connection_url)

def transform_fund_master(engine):

    sql = """
    CREATE TABLE analytics.fund_master AS
    SELECT
        CAST(amfi_code AS INTEGER) AS amfi_code,
        fund_house,
        scheme_name,
        category,
        sub_category,
        plan,
        CAST(NULLIF(launch_date, '') AS DATE) AS launch_date,
        benchmark,
        CAST(NULLIF(expense_ratio_pct, '') AS NUMERIC(8,4)) AS expense_ratio_pct,
        CAST(NULLIF(exit_load_pct, '') AS NUMERIC(8,4)) AS exit_load_pct,
        CAST(NULLIF(min_sip_amount, '') AS NUMERIC(12,2)) AS min_sip_amount,
        CAST(NULLIF(min_lumpsum_amount, '') AS NUMERIC(12,2)) AS min_lumpsum_amount,
        fund_manager,
        risk_category,
        sebi_category_code
    FROM staging.fund_master;
    """

    with engine.begin() as connection:

        connection.execute(text("DROP TABLE IF EXISTS analytics.fund_master"))
        connection.execute(text(sql))
        connection.execute(text("""
            ALTER TABLE analytics.fund_master
            ADD CONSTRAINT pk_fund_master
            PRIMARY KEY (amfi_code)
        """))
        connection.execute(text("""
            ALTER TABLE analytics.fund_master
            ALTER COLUMN fund_house SET NOT NULL,
            ALTER COLUMN scheme_name SET NOT NULL,
            ALTER COLUMN category SET NOT NULL,
            ALTER COLUMN plan SET NOT NULL
        """))


        row_count = connection.execute(text("SELECT COUNT(*) FROM analytics.fund_master")).scalar_one()

        print(f"Analytics fund master created: {row_count} rows")

if __name__ == "__main__":
    engine = create_database_engine()

    try:
        transform_fund_master(engine)
    finally:
        engine.dispose()
        