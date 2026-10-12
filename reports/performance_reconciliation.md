
# Mutual Fund Project V2 — Performance Reconciliation Report

## 1. Objective

Compare the supplied scheme performance metrics against returns independently calculated from the historical NAV dataset.

The purpose is to assess consistency between the two datasets before using the supplied performance metrics in downstream analytics and Power BI reporting.

## 2. Source datasets

| Dataset | File | Purpose |
|---|---|---|
| Fund master | `01_fund_master.csv` | Scheme identifiers and metadata |
| NAV history | `02_nav_history.csv` | Historical NAV observations |
| Scheme performance | `07_scheme_performance.csv` | Supplied return and risk metrics |

The raw CSV files were preserved unchanged during this investigation.

## 3. One-year return methodology

The latest available NAV date is **29 May 2026**. The one-year target date is **29 May 2025**.

For each AMFI code:

1. Select the latest NAV observation on or before the target date.
2. Select the latest NAV observation on or before the latest available date.
3. Calculate the annualized return using the elapsed number of days.

Formula:

\[
R = \left[
\left(\frac{NAV_{\text{end}}}{NAV_{\text{start}}}\right)^{365.25/d} - 1
\right]\times100
\]

where \(d\) is the elapsed number of days between the selected observations.

The difference is defined as:

`calculated return - supplied return`

Differences are expressed in percentage points.

## 4. Data integrity checks

| Check | Result |
|---|---|
| Funds compared | 40 |
| Duplicate fund-date NAV records | 0 |
| AMFI codes matched between performance and fund master | 40 of 40 |
| Scheme-name mismatches | 0 |
| Funds with missing plan classification | 0 |
| Start-date offsets from target date | 0 days for all 40 funds |
| End-date offsets from latest NAV date | 0 days for all 40 funds |

The fund master `plan` column is used for plan classification instead of inferring plan type from scheme names.

## 5. One-year return comparison

| Metric | Result |
|---|---:|
| Funds compared | 40 |
| Mean difference | +5.069 pp |
| Median difference | +4.764 pp |
| Standard deviation of differences | 22.927 pp |
| Minimum difference | -64.789 pp |
| Maximum difference | +58.292 pp |
| Correlation between supplied and calculated returns | 0.107 |

### Largest absolute differences

| Scheme | Supplied return | Calculated return | Difference |
|---|---:|---:|---:|
| Axis Small Cap Fund - Regular - Growth | 21.970% | -42.819% | -64.789 pp |
| SBI Small Cap Fund - Regular Plan - Growth | 24.560% | 82.852% | +58.292 pp |
| ABSL Small Cap Fund - Regular - Growth | 24.930% | -24.000% | -48.930 pp |
| SBI Bluechip Fund - Regular Plan - Growth | 12.420% | 60.489% | +48.069 pp |
| DSP Small Cap Fund - Regular - Growth | 20.200% | 65.195% | +44.995 pp |

## 6. Three-year return comparison

The supplied three-year return metrics were also compared with annualized returns calculated from NAV history.

| Metric | Result |
|---|---:|
| Funds compared | 40 |
| Mean difference | +2.322 pp |
| Median difference | +4.988 pp |
| Standard deviation of differences | 12.689 pp |
| Minimum difference | -32.683 pp |
| Maximum difference | +19.923 pp |
| Correlation between supplied and calculated returns | 0.082 |

The annualized calculation substantially reduced the differences compared with comparing cumulative three-year returns against supplied annualized figures. However, the remaining differences and low correlation indicate that the metrics are not yet reconciled.

## 7. Interpretation and limitations

The investigation found:

- No duplicate fund-date NAV observations.
- Matching AMFI codes and scheme names between the performance file and fund master.
- Exact alignment of the selected NAV dates for the one-year comparison.
- Very weak correlation between supplied and NAV-calculated returns over both periods.

These checks rule out several straightforward data-matching and date-selection explanations. They do not establish the underlying cause of the discrepancies.

Potential explanations still requiring investigation include differences in source-data construction, return conventions, and other methodology differences.

The analysis does not establish that either source dataset is definitively incorrect.

## 8. Decision for downstream analytics

1. Preserve all original raw CSV files unchanged.
2. Do not overwrite supplied performance metrics with calculated values.
3. Keep supplied and calculated returns clearly distinguished.
4. Treat the supplied performance metrics as **not yet reconciled**.
5. Document the limitation before using supplied performance metrics in reporting.
6. Revisit the discrepancies if additional source documentation becomes available.

## 9. Scripts used

- `src/compare_1yr_returns.py`
- `src/compare_3yr_returns.py`
- `src/validation.py`
- `scripts/diagnostics/inspect_nav_sample.py`
- `scripts/diagnostics/check_nav_consistency.py`
- `scripts/diagnostics/check_nav_ranges.py`
- Additional NAV endpoint and date diagnostic scripts in `scripts/diagnostics/`

## 10. Status

**Status: Initial reconciliation completed; discrepancies remain unresolved.**

The initial investigation is documented. The project can proceed to the staging layer provided that the unresolved performance-metric limitation remains explicit and the raw source values are preserved.
