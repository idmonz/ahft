# Helios Nexus Roadmap – v39 "Hyperion Matrix"

> **Vision**  Harness on-chart online learning so that each expert becomes an
> adaptive agent. The ensemble should reason, choose and size trades like a
> discretionary desk while remaining fully executable in Pine v5.

| Phase   | Codename | Objective | New Core Modules | Done-When & KPIs |
| ------- | -------- | --------- | ---------------- | ---------------- |
| **B-0** | **Bandit Ensemble** | Replace static weight blend with a linear
Thompson bandit. Exploit around 12 expert signals and a bias feature as
context. | `bandit_init()` posterior store; `bandit_predict(x)` -> u;
`bandit_update(r)` on trade close. | BTCUSDT 15 m walk-forward 2022-24
Sharpe ≥ 1.35, MDD ≤ 30 %. Unit tests ensure posterior PSD with no NaNs. |
| **B-1** | **Scenario Probabilistic Reasoner (SPR)** | Map expert score
vectors to a latent scenario (trend, chop, squeeze) via an online
softmax classifier. | Dirichlet moment posterior; `spr_sample()` adds a
`scenario_id` feature. | Mutual-info gain vs. v38 ≥ 0.05 bits. |
| **B-2** | **Meta-Policy Gating** | Learn to route between the QR-DQN
λ-scheduler and Kelly-bandit sizing conditioned on scenario and draw-down.
| `gate_score = f(scenario, DD, msgarch)`; soft routing coefficient
α feeds risk sizing. | Correct tool routing ≥ 70 % on replay. |
| **B-3** | **Adaptive Exit Engine 2.0** | Select SL/TP tuple from classic,
trailing or parabola via Thompson bandit on realised reward. | Arrays
`exit_bandit_*` (three arms); reward = delta PNL per risk unit. |
Profit factor ≥ 1.60 on BTC, ETH, SOL 15 m. |
| **B-4** | **Risk Sentinel Fusion** | Fuse AIMRE, LOMV, OI/Funding and
MSGARCH into a single risk state with a Kalman filter. Feed that into
λ bounds and exit veto. | Function `risk_state_kf()` (two variable Kalman). |
False-positive sentinel exits ≤ 3 %. |
| **B-5** | **Live Sim Harness** | CI pipeline replays six symbols across
three timeframes nightly and posts metrics to GitHub PR. |
`scripts/backtest_ci.py` (off-chart). | CI is green if all KPIs pass. |

---

## Pine-Only Constraints

* Learning arrays must stay below 100 KB.
* Avoid `matrix.inverse`; use rank‑1 Sherman‑Morrison updates.
* Sample the posterior via Cholesky on a packed triangle.
* If any step exceeds limits, flag **EXT‑HOOK** so it moves to the
  ONNX phase in v40.

---

## Timeline (two-week iterations)

1. **Week 1‑2** – Bandit Ensemble and back‑test CI skeleton.
2. **Week 3‑4** – Integrate SPR and rerun KPI gate.
3. **Week 5‑6** – Roll out Meta‑Policy Gating and Exit 2.0.
4. **Week 7**   – Risk Sentinel Fusion.
5. **Week 8**   – CI hardening and documentation.

---

## Acceptance Criteria

* Portfolio Sharpe ≥ 1.45 (BTC/ETH/SOL blend, 2021‑25).
* Max draw‑down ≤ 28 %.
* Unit‑test coverage ≥ 80 % for new functions.
* No compile or runtime error on 1 min through 1 D timeframes.

---

## Research References (add to `docs/bibliography.bib`)

* Agarwal & Goyal (2013) – Thompson Sampling for Contextual Bandits.
* Riquelme et al. (2018) – Deep Bayesian Bandits Showdown.
* Cartea et al. (2020) – Algorithmic Trading with Machine Learning.
* Howard et al. (2021) – Time‑Uniform Confidence in Linear Bandits.

---

### Maintainers

| Role                   | GitHub handle       |
| ---------------------- | ------------------- |
| Bandit & SPR core      | `@quantjedi`        |
| Exit 2.0 / Risk Fusion | `@delta-hedger`     |
| CI / Tooling           | `@infra-bot`        |
| Lead reviewer          | `@hephaestus-prime` |

