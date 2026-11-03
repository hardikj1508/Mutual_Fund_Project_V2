# Mutual Fund Analytics V2

An end-to-end mutual fund analytics project built using **Python, PostgreSQL, SQL, and Power BI**. The project transforms raw mutual fund datasets into validated analytical tables, creates reporting views, and presents insights through an interactive five-page dashboard.

## 1. Project Overview

Mutual Fund Analytics V2 is a rebuilt and enhanced version of an earlier mutual fund analysis project.

The objective is to create a structured analytics workflow covering:

- Mutual fund and scheme information
- NAV history and daily returns
- Scheme performance and risk metrics
- Assets under management (AUM)
- SIP inflows and industry folio trends
- Investor transaction activity
- Equity portfolio holdings
- Benchmark index movements

The project uses Python for data processing and validation, PostgreSQL for data storage and SQL-based reporting, and Power BI for interactive analysis and visualization.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion, processing and validation |
| Pandas & NumPy | Data manipulation and numerical operations |
| PostgreSQL | Structured storage and analytical queries |
| SQL | Reporting views and data enrichment |
| Power BI | Interactive dashboard and visualization |
| Excel / CSV | Source data formats |
| Git & GitHub | Version control and project hosting |

## 3. Setup and Execution

### Prerequisites

- Python
- PostgreSQL
- Power BI Desktop
- Git

### Python Environment

Create a virtual environment:

```bash
python -m venv V2env
```

Activate it on Windows:

```bash
V2env\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Database Configuration

- Create the PostgreSQL database.
- Configure the database connection using the project's environment configuration.
- Ensure the required raw datasets are available before running the pipeline.
- Do not commit database passwords, credentials or other sensitive configuration details.

### Project Execution

The project includes Python scripts for the data processing workflow:

1. Data ingestion
2. Staging
3. Transformation
4. Validation

The SQL reporting views are available in `sql/reporting/`.

The Power BI dashboard is available in the `powerbi/` directory.

## 4. Project Architecture

The project follows a layered data workflow:

1. **Raw:** Source CSV datasets.
2. **Staging:** Data loaded into PostgreSQL staging tables.
3. **Analytics:** Processed and structured analytical tables.
4. **Reporting:** SQL views designed for dashboard consumption.

The workflow separates source data, transformation, analytical storage and reporting.

## 5. Dataset Overview

The project contains 10 datasets with a combined **87,533 records**.

| Dataset | Records |
|---|---:|
| Fund Master | 40 |
| NAV History | 46,000 |
| AUM by Fund House | 90 |
| Monthly SIP Inflows | 48 |
| Category Inflows | 144 |
| Industry Folio Count | 21 |
| Scheme Performance | 40 |
| Investor Transactions | 32,778 |
| Portfolio Holdings | 322 |
| Benchmark Indices | 8,050 |
| **Total** | **87,533** |

## 6. Python Processing and Validation

Python scripts handle ingestion, staging, transformation and validation.

Key scripts include:

- `src/ingestion.py` — inventories the available raw CSV files.
- `src/staging.py` — handles staging operations.
- `src/transform.py` — processes data for analytical use.
- `src/validation.py` — performs dataset validation checks.
- `src/compare_1yr_returns.py` — compares supplied and NAV-derived one-year returns.
- `src/compare_3yr_returns.py` — compares supplied and NAV-derived three-year returns.

Validation covers dataset dimensions, distinct identifiers, date coverage and other data-quality checks.

## 7. PostgreSQL Reporting Layer

Four reporting views are created to provide analysis-ready datasets for Power BI.

| Reporting View | Purpose |
|---|---|
| `reporting.vw_fund_overview` | Combines fund details, scheme performance and latest available fund-house AUM |
| `reporting.vw_nav_returns` | Calculates daily NAV returns using SQL window functions |
| `reporting.vw_investor_transactions` | Enriches investor transactions with scheme and fund metadata |
| `reporting.vw_portfolio_holdings` | Enriches portfolio holdings with scheme and fund information |

The reporting layer reduces the need for repeated joins and calculations within Power BI.

## 8. Power BI Dashboard

The interactive dashboard contains five analytical pages:

1. **Market Overview** — overall mutual fund market indicators and trends.
2. **Fund Performance** — scheme returns across one-year, three-year and five-year horizons.
3. **Risk Analysis** — scheme risk and risk-adjusted performance metrics.
4. **Investor Activity** — transaction trends, investor demographics and transaction characteristics.
5. **Portfolio & Holdings** — portfolio composition, sector exposure and holdings analysis.

The report includes interactive slicers, cross-page filtering where applicable, KPI cards and drill-down analysis.

## 9. Data Validation and Performance Reconciliation

The project compares supplied scheme performance figures against returns calculated from NAV history.

The reconciliation covered 40 funds.

| Metric | 1-Year Comparison | 3-Year Comparison |
|---|---:|---:|
| Mean difference (percentage points) | +5.069 | +2.322 |
| Median difference (percentage points) | +4.764 | +4.988 |
| Standard deviation (percentage points) | 22.927 | 12.689 |
| Correlation | 0.107 | 0.082 |

The comparison identified material differences between supplied performance metrics and NAV-derived returns.

The underlying cause has not been established. Original supplied values are preserved, and calculated returns are maintained separately rather than silently replacing or reconciling the source figures.

Additional details are available in `reports/performance_reconciliation.md`.

## 10. Data Limitations and Assumptions

- Investor transaction records are synthetic and should not be interpreted as actual customer transactions.
- Portfolio holdings represent a snapshot rather than continuously updated holdings.
- Monthly SIP inflows represent market-wide data and are not fund-house-specific.
- Supplied scheme performance figures differ from NAV-derived calculations. These differences remain documented and unresolved.
- Fund-house AUM values use the latest available record for each fund house; reporting dates may differ between fund houses.
- Raw source datasets are excluded from the repository and must be obtained separately to reproduce the complete pipeline.

## 11. Repository Structure

```text
Mutual_Fund_Project_V2/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── powerbi/
│   └── Mutual_Fund_Dashboard.pbix
│
├── reports/
│   └── performance_reconciliation.md
│
├── scripts/
│   └── diagnostics/
│
├── sql/
│   └── reporting/
│       ├── vw_fund_overview.sql
│       ├── vw_nav_returns.sql
│       ├── vw_investor_transactions.sql
│       └── vw_portfolio_holdings.sql
│
├── src/
│   ├── ingestion.py
│   ├── staging.py
│   ├── transform.py
│   ├── validation.py
│   ├── compare_1yr_returns.py
│   └── compare_3yr_returns.py
│
├── .gitignore
└── requirements.txt
```

## 12. Project Status

The data processing pipeline, PostgreSQL reporting layer and five-page Power BI dashboard have been developed. The project is currently in its documentation and repository preparation stage.