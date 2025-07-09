#!/usr/bin/env python3
# Auto-generates the strategy table in README.md from scripts/
import pathlib, re, sys, datetime
repo = pathlib.Path(__file__).resolve().parent.parent
scripts = sorted(repo.glob("scripts/AHFT-HPH-v*.pine"), key=lambda p: p.name, reverse=True)
table = ["| File | Version | Date |","|------|---------|------|"]
rx = re.compile(r"v(\d+\.\d+r?-?\d?)")
for p in scripts:
    ver = rx.search(p.name).group(1)
    date = datetime.date.today().isoformat()
    table.append(f"| `{p.name}` | `{ver}` | {date} |")
readme = repo/"README.md"
content = readme.read_text(encoding="utf-8")
head, sep, rest = content.partition("## Strategy index")
if not sep:
    sys.exit("README missing 'Strategy index' section")
rest = re.sub(r'^\n?(?:\|.*\n)+', '', rest, flags=re.MULTILINE)
rest = rest.lstrip("\n")
readme.write_text(head + "## Strategy index\n" + "\n".join(table) + "\n" + rest, encoding="utf-8")
