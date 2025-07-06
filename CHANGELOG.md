# Changelog
## v38.4-r1 "Helios Nexus Patch 4" - 2025-07-10
- Added Bayesian parameter search and improved DistRL transfer.
- Optimized commission gate with contract value check.
- Risk floor now scales with CVaR rank.

## v38.3.0 "Helios Nexus Patch 3" - 2025-07-09
- Implemented size-aware commission gate and multi-symbol DistRL.
- Added decay factor for QR-DQN histogram.

## v38.2r-1 "Helios Nexus Patch 2 Hotfix" - 2025-07-08
- Fixed commission threshold bug causing compilation error.
- No functional changes other than bug fix.
## v38.2.0 "Helios Nexus Patch 2" - 2025-07-08
- Added commission-aware entry gate and higher meta-exit threshold.
- Volatility floor raised to 0.15 and TP reduction scaled back.
- Enabled QR-DQN and CVaR ε-greedy by default.

## v38.1.0 "Helios Nexus Patch" - 2025-07-07
- Rebalanced TP/SL multipliers by volatility.
- Tightened meta-exit threshold to 0.90 with severity filter.
- Corrected risk per unit using ATR.
- Increased drawdown φ default to 3.0.


## v38.0.0 "Helios Nexus" - 2025-07-06

- Integrated QR-DQN distributional RL with safe array checks.
- Added CVaR ε-greedy exploration and drawdown-aware Kelly sizing.
- Introduced MSGARCH regime limits and refined λ risk budget.
- Built from v37.9.4 without weakening existing logic.

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
