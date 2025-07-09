# Helios Nexus Pine Overview

This document explains the Pine-only architecture of AHFT v38.9.0 and how to use
Optuna calibration blobs.

## Inside-TV Architecture

```
+------------+    +---------------+
|  Market    | -> |  AHFT Script  |
+------------+    +---------------+
        |                  |
        v                  v
  DistRL Buffer     Adaptive Weights
        |                  |
        +-------> Decision Engine
```

All computation stays within TradingView. External training or inference is not
required for the v38 release.

## Using Optuna Calibration

1. Run your optimizer externally and copy the resulting JSON blob.
2. In TradingView, open the script settings and paste the blob into the
   `calib_blob` input string.
3. On the next bar the strategy will parse the parameters and apply them.
