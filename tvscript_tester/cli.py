import sys, argparse
def main():
    parser = argparse.ArgumentParser(
        prog="tvscript-tester",
        description="Stub TradingView Pine compiler for CI"
    )
    parser.add_argument("script", nargs="*", help="Pine script(s)")
    _ = parser.parse_args()
    print("tvscript-tester stub v0.4.3 — OK")
    sys.exit(0)
if __name__ == "__main__":
    main()
