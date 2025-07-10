#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(git rev-parse --show-toplevel)"
pip install --no-index --find-links="$ROOT_DIR/external" tvscript-tester==0.4.3
