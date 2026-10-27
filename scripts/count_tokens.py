#!/usr/bin/env python3
"""Estimate context size. Usage: count_tokens.py FILE_OR_DIR [...] [--budget 8000]
Estimate = characters / 4 (rough rule for English and code). Use it to compare variants, not for billing."""
import argparse, pathlib, sys

def files(paths):
    for p in map(pathlib.Path, paths):
        yield from ([p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and ".git" not in x.parts and "__pycache__" not in x.parts))

ap = argparse.ArgumentParser(); ap.add_argument("paths", nargs="+"); ap.add_argument("--budget", type=int, default=0)
a = ap.parse_args(); rows = []
for f in files(a.paths):
    try: rows.append((len(f.read_text(errors="ignore")) // 4, str(f)))
    except Exception: pass
rows.sort(reverse=True)
for n, name in rows[:15]: print(f"{n:>7}  {name}")
total = sum(n for n, _ in rows); print(f"{total:>7}  TOTAL (estimated tokens)")
if a.budget and total > a.budget: print(f"OVER BUDGET by {total - a.budget}"); sys.exit(1)
