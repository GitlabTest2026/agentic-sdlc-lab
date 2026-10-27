#!/usr/bin/env python3
"""Fail if pyproject.toml gains a dependency compared with a base ref. Usage: check_no_new_deps.py [base_ref]"""
import subprocess, sys, tomllib

base = sys.argv[1] if len(sys.argv) > 1 else "origin/lab-start"

def deps(text: str) -> set[str]:
    d = tomllib.loads(text)
    out = set(d["project"].get("dependencies", []))
    for group in d["project"].get("optional-dependencies", {}).values():
        out |= set(group)
    return {x.split("==")[0].split(">")[0].split("<")[0].strip().lower() for x in out}

old = deps(subprocess.run(["git", "show", f"{base}:pyproject.toml"], capture_output=True, text=True, check=True).stdout)
new = deps(open("pyproject.toml").read())
added = sorted(new - old)
if added:
    print("NEW DEPENDENCIES NOT ALLOWED:", ", ".join(added)); sys.exit(1)
print("ok: no new dependencies")
