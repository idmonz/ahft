# Helios Nexus Road‑map  (v38 line)

> **Updated:** 2025‑07‑09  |  Maintainers: *AHFT‑Core Guild*

---

### Release track

| Tag                   | Date       | Summary                                                                                   |
| --------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| **v38.0.0**           | 2025‑07‑06 | Helios Nexus GA – QR‑DQN kernel, MSGARCH‑GJR λ‑clamp, risk capsule, deterministic seeding |
| **v38.6.0**           | 2025‑07‑07 | Refined entry thresholds, leverage clamp                                                  |
| **v38.7.0**           | 2025‑07‑08 | Lagged OBI, deterministic seed hot‑patch                                                  |
| **v38.8r‑3**          | 2025‑07‑09 | Dynamic weight floor, AIMRE auto‑threshold, QR‑DQN index fix                              |
| **v38.8r‑4 *(next)*** | **TBD**    | AIMRE bug‑fix, correlation‑aware AOML, QR‑DQN parametrisation, code modularisation        |

---

### Programme status matrix

| Phase   | Goal                             | Completion       | Notes                                                                            |
| ------- | -------------------------------- | ---------------- | -------------------------------------------------------------------------------- |
| **P‑1** | Safe‑array wrapper               | **✅**            | All `array.get` now routed through `f_safe_array_get` & unit replay tests green. |
| **P‑2** | Distributional RL (QR‑DQN)       | **✅**            | 32‑quantile engine live; further parameterisation scheduled for r‑4.             |
| **P‑3** | Regime model 2.0                 | **✅**            | MSGARCH‑GJR drives λ bounds (0.3–2.5).                                           |
| **P‑4** | Bayesian Auto‑Tune pipeline      | **🟡 Partial**   | Thompson‑softmax & variant DB live; Optuna export CLI still WIP.                 |
| **P‑5** | Drawdown‑aware Kelly κ(t)        | **✅**            | κ shrink & dynamic floor shipped in r‑3.                                         |
| **P‑6** | Multi‑symbol DistRL transfer     | **✅**            | BTC / ETH / SOL enabled; weight `DISTRL_XFER_W` exposed.                         |
| **P‑7** | ONNX / Wasm backend mock         | **🟡 Prototype** | Pine → Wasm PoC compiles; benchmark harness pending.                             |
| **P‑8** | *Stabilisation & Modularisation* | **🚧 (r‑4)**     | AIMRE fix, expert‑corr penalty, QR‑DQN cfg input, regression CI.                 |

> Legend: **✅ Done** · **🟡 Partial** · **🚧 In progress**

---

## Sprint r‑4  (ETA 2025‑07‑12)

| ID      | Work‑item                                                       | Owner       | Acceptance test                                         |   |        |
| ------- | --------------------------------------------------------------- | ----------- | ------------------------------------------------------- | - | ------ |
| **S‑1** | **AIMRE sentinel patch** – correct scope leak, min‑sample guard | @quant‑fx   | Exits attributed to AIMRE ≥ 3 % in 2023 BTC‑15m replay  |   |        |
| **S‑2** | Correlation‑aware AOML update                                   | @ai‑lambda  | Weight drift Δ ≤ 5 % when                               | ρ |  > 0.8 |
| **S‑3** | QR‑DQN parameterisation (`NUM_Q`, LR decay)                     | @rl‑dev     | Back‑test Sharpe change ≤ ±2 % vs r‑3 baseline          |   |        |
| **S‑4** | Codebase modular split (experts / risk / ui)                    | @core‑infra | Build passes, no perf regression (≤ 1 %)                |   |        |
| **S‑5** | Regression CI docker pipeline                                   | @dev‑ops    | 3‑year walk‑forward finishes < 30 min inside GH‑Actions |   |        |
| **S‑6** | Docs: "Risk Capsule Playbook"                                   | @docs‑team  | Merge‑request approved by guild lead                    |   |        |

---

## Looking ahead – v39 pre‑planning

* **Adaptive Symbol Discovery** – automatic addition of new perp tickers with liquidity & latency filters.
* **Transformer‑based latent encoder** replacing Patch‑TST (prototype branch `xform‑tst`).
* **Real‑time WASM inference** on Kraken futures feed (target latency < 5 ms per bar).
* **Portfolio‑level CVaR optimiser** for multi‑asset risk envelope.

> *Suggestions & pull‑requests welcome – open an issue or ping us on #helios‑research.*

---

© 2025 AHFT Labs – released under the AGPL‑3.0
