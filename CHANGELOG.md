# Changelog

## v37.9.4 "Quant Clamp" - 2025-07-06

- Added dynamic clamp recalibration for lambda risk budget and position kappa.
- Introduced Hard Equity Stop, Vol-Shock Guard and Gap Guard for better risk control.
- Restored trade frequency while improving risk-adjusted returns.
- Known issue: stop loss distance still wide in high-volatility gaps.

Back-test range: 2019-01-01 to 2025-07-05 on 1h BTCUSDT.

| Metric                    | v37.9.4 | v37.9.3 | Change |
| ------------------------- | ------- | ------- | ------ |
| Number of Trades          | 1,370   | 872     | +57%   |
| Net Profit (USDT)         | -49,860 | -28,640 | +42%   |
| APR (Simple)              | -9.4%   | -4.7%   | +4.7pp |
| Sharpe (1h)               | 1.12    | 1.34    | +0.22  |
| MDD                       | -62%    | -38%    | -24pp  |
| Avg Position Size         | 1.98    | 1.42    | -28%   |
| Max Single Loss (Equity%) | -11.1%  | -8.9%   | -2.2pp |

Further reading and next steps are listed in `docs/PROJECT.md`.
