#!/usr/bin/env python3
"""Summarize experiments/results.csv per variant. Usage: summarize.py [experiments/results.csv]"""
import csv, sys, collections
rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "experiments/results.csv")))
g = collections.defaultdict(list)
for r in rows: g[r["variant"]].append(r)
print(f"{'variant':8}{'runs':>5}{'hidden_pass%':>14}{'existing_ok%':>14}{'avg_lines':>11}{'avg_min':>9}{'corrections':>13}")
for v, rs in sorted(g.items()):
    n = len(rs); p = lambda k: 100 * sum(r[k] == "True" for r in rs) / n
    mins = [float(r["minutes"]) for r in rs if r["minutes"]]
    print(f"{v:8}{n:>5}{p('hidden_pass'):>14.0f}{p('existing_tests_pass'):>14.0f}{sum(int(r['lines_changed']) for r in rs)/n:>11.1f}{(sum(mins)/len(mins) if mins else 0):>9.1f}{sum(int(r['human_corrections'] or 0) for r in rs):>13}")
