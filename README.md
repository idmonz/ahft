# AHFT Hephaestus-Prime

This repository hosts the Pine Script implementation and documentation for the
AHFT Hephaestus-Prime project. Strategy scripts live in `scripts/` and the
project documents live under `docs/`.

## Layout
- `scripts/AHFT-HPH-v38.8r-4.pine` – current strategy release
- `scripts/AHFT-HPH-v38.8r-3.pine` – previous hotfix
- `scripts/AHFT-HPH-v38.8r-2.pine` – earlier hotfix
- `scripts/AHFT-HPH-v38.8r-1.pine` – first hotfix
- `scripts/AHFT-HPH-v38.8.0.pine` – base release
- `docs/PROJECT.md` – background, architecture and user guides
- `docs/CHARTER.md` – development doctrine and historical notes
- `CHANGELOG.md` – version history

Version 38.8.0 integrates the new LOMV and AIMRE engines, swaps to an IQN risk model and adds a HAR-RV volatility regime.
Version 38.8r-1 fixes weight normalization for the LOMV module and adjusts the QR-DQN update index.

Version 38.8r-2 corrects weight floor placement and raises the AIMRE sentinel threshold to 3.0.

Version 38.8r-3 introduces a dynamic weight floor and auto-calibrated AIMRE threshold.
Version 38.8r-4 fixes the AIMRE sentinel bug and adds correlation-aware AOML.

Version 38.7r-3 introduces stubs for Pseudo-BO and Patch-Lite to prepare upcoming optimization and fine-tuning modules.
Version 38.7r-2 fixes deterministic seed initialization after a compile error. Version 38.7.0 introduces deterministic random seeding, lagged order-book imbalance and a final take profit at 4R. Version 38.6r-1 fixes a function definition error in v38.6.0. Version 38.6.0 tweaks risk thresholds with a 0.4% risk floor, dynamic leverage clamp and order-book feature. Version 38.5.0 introduces a risk capsule, partial exits and expanded Bayesian variants. Version 38.4-r1 introduces Bayesian parameter tuning and improved DistRL transfer. Version 38.3.0 adds multi-symbol transfer learning and size-aware commission gating. Version 38.2r-1 fixes commission threshold calculation. The original 38.2.0 release added commission-aware entry gating and refined meta-exit logic. Version 38.1.0 ("Helios Nexus Patch") adds refined risk controls.
See `CHANGELOG.md` for details.
The v38 release, codenamed "Helios Nexus", is detailed in
`docs/ROADMAP_v38.md`.

