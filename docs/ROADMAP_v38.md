# Helios Nexus Roadmap (v38)


**Status**: Completed with the release of v38.0.0 on 2025-07-06. Patch v38.8r-3 adds a dynamic weight floor and AIMRE auto threshold. Patch v38.8r-1 fixed weight normalisation and QR‑DQN indexing. Patch v38.7r-3 adds Pseudo-BO and Patch-Lite stubs. Patch v38.7r-2 replaces the seed call for older builds. Patch v38.7r-1 fixed deterministic seed initialization. Patch v38.7.0 adds deterministic seeding, lagged OBI and a 4R take profit. Patch v38.6r-1 fixes a compile error in patch 6. Patch v38.6.0 introduces refined entry thresholds and leverage clamp. Patch v38.5.0 introduces a risk capsule and partial exits. Patch v38.4-r1 adds Bayesian tuning and transfer improvements. Patch v38.3.0 adds multi-symbol DistRL and commission-gate fixes; v38.2r-1 fixed commission handling and v38.2.0 refined risk controls.


The v38 major update, codenamed **"Helios Nexus"**, introduces a structured
series of enhancements. Each phase has concrete goals and validation steps.

| Phase | Goal | Key Modules | Deliverables & Verification |
| ---- | ---- | ----------- | --------------------------- |
| **P-1** | Remove all `array.get` boundary errors | Safe array wrapper `safe_get(arr,i,def)` | LEAK-WATCH unit tests, full replay from 1m to 1D with no errors |
| **P-2** | Distributional RL engine | Replace ε-Greedy skeleton with QR‑DQN; CVaR ε‑greedy option | Sharpe ≥ v37.8 +15% on BTCUSDT 15m back-test |
| **P-3** | Regime model 2.0 | MSGARCH-GJR two-state volatility model feeding λ-scaler | Overnight gap MSE reduced 20% |
| **P-4** | Bayesian Auto-Tune | Optuna/BoTorch hyperparameter pipeline | Out-of-sample Sharpe ≥ 0.75 × in-sample result |
| **P-5** | Capital management | Drawdown-aware fractional Kelly κ(t) | MDD < 30% while preserving CAGR |
| **P-6** | Multi-symbol transfer learning | Shared DistRL head for BTC, ETH, SOL | Additional symbols maintain Sharpe ≥ 1.2 |
| **P-7** | Performance & deployment | ONNX/Wasm backend mock with GPU inference bench | 4H test executes 10× faster |

Core design notes:

- **Safe array pattern** uses `safe_get` to guard every `array.get` call and avoid index errors across timeframes.
- **Distributional RL to Risk Budget** – QR‑DQN quantiles feed λ‑Scheduler for CVaR based sizing.
- **MSGARCH-GJR** states limit λ ranges: low-vol ≤ 1.2, high-vol ≥ 0.3.
- **Adaptive κ-Kelly** – fractional κ shrinks with drawdown: κ(t)=κ₀·e^(−DD·φ).
- **Bayesian Auto-Tune** – Optuna TPE converges within ~50 trials; optimal parameters exported to Pine inputs.

Reference papers are listed in `docs/bibliography.bib`.
