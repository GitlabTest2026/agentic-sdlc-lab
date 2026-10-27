#!/usr/bin/env python3
"""Show which CODEOWNERS rule covers each changed file (a simplified local approximation; GitHub is the source of truth).
Usage: codeowners_check.py [--base BRANCH]            files changed vs BRANCH (default lab-start)
       codeowners_check.py --paths a/b.py c/d.yml     check explicit paths"""
import fnmatch, subprocess, sys

def load(path=".github/CODEOWNERS"):
    rules = []
    for line in open(path):
        line = line.split("#")[0].strip()
        if line:
            pat, *owners = line.split(); rules.append((pat, owners))
    return rules

def matches(pat, path):
    anchored, p = pat.startswith("/"), pat.lstrip("/")
    if p.endswith("/"): return path.startswith(p) if anchored else p in path
    return fnmatch.fnmatch(path, p) if anchored else fnmatch.fnmatch(path.split("/")[-1], p)

def owner_for(path, rules):
    hit = None
    for pat, owners in rules:          # the last matching rule wins, as on GitHub
        if matches(pat, path): hit = (pat, owners)
    return hit

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--paths"]: paths = a[1:]
    else:
        base = a[1] if a[:1] == ["--base"] else "lab-start"
        paths = subprocess.run(["git", "diff", "--name-only", base], capture_output=True, text=True, check=True).stdout.split()
    rules, review = load(), 0
    for p in paths:
        hit = owner_for(p, rules)
        if hit: review += 1; print(f"REVIEW REQUIRED  {p:45} <- {hit[0]} {' '.join(hit[1])}")
        else: print(f"no code owner    {p}")
    print(f"\n{review} of {len(paths)} changed files need code-owner review")
    sys.exit(0)
