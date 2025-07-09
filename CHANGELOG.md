# Changelog

## v38.9.0-pine – 2025-07-21
- Helios Nexus Pine milestone freeze
- CALIB_BLOB 파싱 실패 시 런타임 기본값으로 자동 폴백
- dist_arr 동적 리사이즈가 NUM_Q 변경을 1 bar 이내에 반영
## v38.8r-6 "Helios Nexus Hotfix 6" – 2025-07-23
- CALIB_BLOB 파싱 실패 시 런타임 기본값으로 자동 폴백
- dist_arr 동적 리사이즈가 NUM_Q 변경을 1 bar 이내에 반영

## v38.8r-5 "Helios Nexus Hotfix 5" – 2025-07-22
- dist_arr resize guard 추가로 QR-DQN 버퍼 오버런 방지
- ahft_utils 라이브러리 버전을 1.0으로 고정
## v38.8r-4 "Helios Nexus Patch 8 Hotfix 4" - 2025-07-18
- Fixed AIMRE sentinel scoping bug and added a minimum-sample guard
- Added correlation-aware AOML penalty

## v38.8r-3 "Helios Nexus Patch 8 Hotfix 3" - 2025-07-17
- Introduced dynamic weight floor based on drawdown
- AIMRE sentinel threshold now auto-calibrates
- Dashboard rows expanded for future LOMV stats
- Removed unused pre_norm_total variable

## v38.8r-2 "Helios Nexus Patch 8 Hotfix 2" - 2025-07-16
- Fixed weight floor logic so weights renormalize each bar
- Raised AIMRE sentinel threshold to 3.0
- Defaulted Pseudo-BO and Patch-Lite stubs to false



## v38.8r-1 "Helios Nexus Patch 8 Hotfix" - 2025-07-15
- Fixed weight normalisation for the new LOMV engine and corrected QR-DQN index modulo.

## v38.8.0 "Helios Nexus Patch 8" - 2025-07-14
- Integrated Langlands‑Operadic Möbius Vortex and AIMRE sentinel modules.
- Swapped QR‑DQN head for Implicit Quantile Network with 32 τ grid.
- Added HAR‑RV based TP/SL regime mapping and updated deterministic RNG hooks.
## v38.7r-3 "Helios Nexus Patch 7 Update" - 2025-07-13
- Added Pseudo-BO and Patch-Lite stubs for upcoming optimization modules.
## v38.7r-2 "Helios Nexus Patch 7 Hotfix" - 2025-07-13
- Replaced unsupported `math.seed` with a custom LCG for compatibility.

## v38.7r-1 "Helios Nexus Patch 7 Hotfix" - 2025-07-13
- Fixed missing `math.seed` call and day-of-year reference for deterministic PRNG.
## v38.7.0 "Helios Nexus Patch 7" - 2025-07-13
- Added deterministic random seed initialization for reproducible runs.
- Enabled lagged order-book imbalance on the 15m feed and added a 4R take profit.

## v38.6r-1 "Helios Nexus Patch 6 Hotfix" - 2025-07-12
- Fixed a function definition error that caused compilation failure in v38.6.0.
## v38.6.0 "Helios Nexus Patch 6" - 2025-07-12
- Reduced risk floor to 0.4% equity and added dynamic leverage clamp.
- Entry threshold now uses 75th percentile of signal history.
- Variants explore more with τ=0.25 and α,β=0.5.
- Partial exits occur at 0.8R and 1.6R; added order-book imbalance feature.
## v38.5.0 "Helios Nexus Patch 5" - 2025-07-11
- Introduced risk capsule sizing and partial exit at 1:1 R:R.
- Expanded Thompson variants and tuned reward scaling.
- Lambda floor logic refined for stability.
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

