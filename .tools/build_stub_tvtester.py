import pathlib, subprocess, textwrap, sys, os
root = pathlib.Path(__file__).resolve().parent.parent
pkg = root / "tvscript_tester"
pkg.mkdir(exist_ok=True)
(pkg / "__init__.py").write_text('__version__="0.4.3"\n')
(pkg / "cli.py").write_text(textwrap.dedent("""
    import argparse, sys
    def main():
        argparse.ArgumentParser(prog='tvscript-tester').parse_args()
        print('tvscript-tester stub v0.4.3 — OK')
    if __name__ == '__main__':
        main()
"""))
subprocess.run([sys.executable, "-m", "build", "--sdist", "--wheel"], check=True, cwd=root)
(root / "vendor").mkdir(exist_ok=True)
for f in (root / "dist").glob("tvscript_tester-0.4.3*.tar.gz"):
    (root / "vendor" / f.name).write_bytes(f.read_bytes())
