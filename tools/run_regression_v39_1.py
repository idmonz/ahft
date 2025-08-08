#!/usr/bin/env python3
import argparse, subprocess, sys, os, datetime as dt

DEFAULT_SCRIPT = "scripts/AHFT-CompositeMicro-v39.1.pine"
DEFAULT_CFG    = "configs/baseline_v39.1.pineconfig"
DEFAULT_SYMS   = ["BINANCE:BTCUSDT"]
DEFAULT_TFS    = ["240","60","15"]

def run_once(script, cfg, sym, tfs, start, end, outdir):
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"v39_1_{sym.replace(':','_')}_{'-'.join(tfs)}.html")
    cmd = [
        sys.executable, "-m", "tvscript_tester.run",
        "--script", script,
        "--config", cfg,
        "--symbols", sym,
        "--timeframes", ",".join(tfs),
        "--start", start,
        "--end", end,
        "--report", out,
    ]
    print(">>", " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("WARNING: tvscript_tester failed. Proceeding without report.", file=sys.stderr)
        return None
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=DEFAULT_SCRIPT)
    ap.add_argument("--config", default=DEFAULT_CFG)
    ap.add_argument("--symbols", nargs="+", default=DEFAULT_SYMS)
    ap.add_argument("--timeframes", nargs="+", default=DEFAULT_TFS)
    ap.add_argument("--start", default="2023-01-01")
    ap.add_argument("--end", default=dt.date.today().isoformat())
    ap.add_argument("--outdir", default="reports")
    args = ap.parse_args()

    reports = []
    for s in args.symbols:
        r = run_once(args.script, args.config, s, args.timeframes, args.start, args.end, args.outdir)
        if r: reports.append(r)

    print("\nGenerated reports:")
    for r in reports:
        print(" -", r)

if __name__ == "__main__":
    main()
