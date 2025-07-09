# Helios Nexus Road‑map  (v38 line)

> **Updated:** 2025‑07‑21  |  Maintainers: *AHFT‑Core Guild*

---

### Release track

| Tag                   | Date       | Summary                                                                                   |
| --------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| **v38.0.0**           | 2025‑07‑06 | Helios Nexus GA – QR‑DQN kernel, MSGARCH‑GJR λ‑clamp, risk capsule, deterministic seeding |
| **v38.6.0**           | 2025‑07‑07 | Refined entry thresholds, leverage clamp                                                  |
| **v38.7.0**           | 2025‑07‑08 | Lagged OBI, deterministic seed hot‑patch                                                  |
| **v38.8r‑3**          | 2025‑07‑09 | Dynamic weight floor, AIMRE auto‑threshold, QR‑DQN index fix                              |
| **v38.8r‑4**          | 2025‑07‑18 | AIMRE bug‑fix, correlation‑aware AOML, QR‑DQN parametrisation, code modularisation        |
| **v38.8r‑5**          | 2025‑07‑21 | DistRL lambda bug-fix, utils library update                                               |
| **v38.9.0**           | 2025-07-20 | Pine-only milestone complete; v39 starts |

---

### ✍️ Re-scoped Helios Nexus Road-map

**Focus:** *Everything that can run inside TradingView Pine v5 today.*
**Deferred:** Python/Optuna training, ONNX/Wasm inference, GPU acceleration.

| Tier                                           | Original Goal                                            | Pine-Only Equivalent (2025Q3 sprint)                                                                  | Notes / What we’ll stub                                                                           |
| ---------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **P-1 Safe Array**                             | Guard every `array.get`                                  | ✅ already implemented as `f_safe_array_get` & static unit-replay macro.                               | done                                                                                              |
| **P-2 DistRL**                                 | QR-DQN + CVaR ε-Greedy                                   | **Light-weight quantile buffer** (`dist_arr`) + EWMA reward; keep Thompson-softmax & CVaR ε-Greedy.   | Training of a deep QR-DQN network is postponed; we emulate with 32-slot histogram updated online. |
| **P-3 Regime 2.0**                             | Full MSGARCH-GJR fit                                     | **Proxy regime** (`f_msgarch_regime_proxy`) using rolling `vol-of-vol` & trend corr.                  | GJR parameter estimation to be fitted offline later; leave hook `MSGARCH_CALIB_JSON`.             |
| **P-4 Bayesian Auto-Tune**                     | Optuna/BoTorch pipeline                                  | **In-chart AOML** (adaptive weights) + manual param inputs; keep `USE_PSEUDO_BO` stub.                | Add `input.string calib_blob` so tuned params can be copy-pasted later.                           |
| **P-5 Capital κ(t)**                           | Kelly with drawdown                                      | ✅ `κ(t)=κ₀·e^(-DD·φ)` already live; add dynamic floor.                                                | none                                                                                              |
| **P-6 Multi-symbol Xfer**                      | Shared DistRL head                                       | **Correlation-weighted reward transfer** (`f_transfer_qrdqn`) between symbols via `request.security`. | Shared neural head deferred.                                                                      |
| **P-7 Perf/Deployment**                        | ONNX/Wasm backend                                        | **No action in Pine.** Provide `// TODO: ONNX_INFERENCE()` stub & config flags.                       | All heavy compute deferred.                                                                       |
| **NEW P-8 Stabilisation**                      | —                                                        | • Compile-time pragma checks                                                                          |                                                                                                   |
| • `#ifdef TV_DEBUG` style logging macro        |                                                          |                                                                                                       |                                                                                                   |
| • Regression harness on 1 m / 5 m / 15 m bars. | Keeps Pine side rock-solid before adding external hooks. |                                                                                                       |                                                                                                   |

---

## Concrete TODO list (Pine-only sprint)

1. **Modularise helper file** – ✅
   Create `library/ahft_utils.pine` for: safe array, clamp, z-score, percentile, etc.
   → Easier to freeze the API before external binding.

2. **Replace magic numbers with `const`** – ✅
   Particularly the AIMRE sentinel blend weights; expose as `input.float` with sensible defaults.

3. **AIMRE auto-threshold polishing** – ✅

   * Maintain a rolling `sentinel_hist` length = `input.int("AIMRE Window",200)`
   * Compute percentile with `ta.percentile` once per bar to avoid unnecessary CPU.

4. **DistRL buffer sanitation** – ✅

   * Clip `rew` into ±5 σ to prevent exploding quantiles.
   * Add `plot(series=dist_arr[ct_count % NUM_Q])` behind `input.bool("Debug DistRL", false)`.

5. **Weight-floor hot-reload** – ✅
   Dynamic floor already added; ensure it survives `strategy.reset()`. Wrap in `varip`.

6. **Regression pack** – ✅

   * Pre-save parameter sets (baseline v38.8r-5) in the repo as `.pineconfig`.
   * Add GitHub Action that runs the strategy with `tvscript-tester` on BTC 1 m / 5 m / 15 m 2022-23 and asserts:

     ```yaml
     sharpe:  >= 1.25
     max_dd:  <= 0.28
     closed_trades: >= 300
     ```

7. **Documentation pass** – ✅
   Update `docs/Helios_Nexus_Pine.md` with:

   * “Inside-TV” architecture diagram
   * How to paste Optuna blobs into `input.string calib_blob`

---

## Deferred (external) items – parking lot

| Item                 | What we *don’t* touch now | Placeholder in code      |
| -------------------- | ------------------------- | ------------------------ |
| QR-DQN training loop | PyTorch + Optuna script   | `// TRAIN_QRDQN.py` link |
| MSGARCH calibration  | `statsmodels`/`arch` fit  | `MSGARCH_CALIB_JSON`     |
| ONNX/Wasm            | Convert model, bench      | `ONNX_INFERENCE()` no-op |

---

## Acceptance criteria for Pine-only milestone (tag: `v38.9.0-pine`)

* **No runtime error** on 1 m→1 D back-replay 2020-2025.
* **AIMRE exit** triggers < 3 % false-positives on 2 yr of BTCUSDT.
* **Performance**: Sim-speed ≥ 12 k bars/s on TV desktop.
* **Metrics** (BTC 15 m 2022-2024): Sharpe ≥ 1.3, MDD ≤ 28 %.

On passing those gates, we lock the Pine side and start the external training/inference track.

---

*This plan keeps immediate progress visible in TradingView while leaving clean hooks for the heavier Python / ONNX stack.*

Next steps are tracked in `docs/ROADMAP_v39.md`.

© 2025 AHFT Labs – released under the AGPL‑3.0
