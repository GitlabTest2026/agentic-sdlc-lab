#!/usr/bin/env python3
"""Score one agent run against the hidden test for a task and append to experiments/results.csv.
Usage: run_eval.py --task t1 --variant A --run 1 --branch copilot/fix-1 [--base lab-start] [--minutes 4.5] [--corrections 0]"""
import argparse, csv, pathlib, re, shutil, subprocess, tempfile, os

ap = argparse.ArgumentParser()
for k in ("task", "variant", "run", "branch"): ap.add_argument("--" + k, required=True)
ap.add_argument("--base", default="lab-start"); ap.add_argument("--minutes", default=""); ap.add_argument("--corrections", default="0")
a = ap.parse_args()
sh = lambda *c, **k: subprocess.run(c, capture_output=True, text=True, **k)

wt = tempfile.mkdtemp(prefix="eval-")
sh("git", "worktree", "add", "--detach", wt, a.branch)
hidden = next(pathlib.Path("eval/hidden").glob(f"test_{a.task}_*.py"))
shutil.copy(hidden, pathlib.Path(wt) / "tests/unit" / hidden.name)
r = sh("python", "-m", "pytest", f"tests/unit/{hidden.name}", "-q", cwd=wt, env={**os.environ, "AUTH_JWT_SECRET_KEY": "x"})
full = sh("python", "-m", "pytest", "tests/unit", "-q", "--ignore", f"tests/unit/{hidden.name}", cwd=wt, env={**os.environ, "AUTH_JWT_SECRET_KEY": "x"})
stat = sh("git", "diff", "--shortstat", f"{a.base}..{a.branch}").stdout
changed = sum(int(x) for x in re.findall(r"(\d+) (?:insertion|deletion)", stat))
sh("git", "worktree", "remove", "--force", wt)

out = pathlib.Path("experiments/results.csv"); out.parent.mkdir(exist_ok=True)
new = not out.exists()
with out.open("a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["task", "variant", "run", "hidden_pass", "existing_tests_pass", "lines_changed", "minutes", "human_corrections"])
    w.writerow([a.task, a.variant, a.run, r.returncode == 0, full.returncode == 0, changed, a.minutes, a.corrections])
print(f"{a.task} {a.variant}#{a.run}: hidden={'PASS' if r.returncode == 0 else 'FAIL'} existing={'PASS' if full.returncode == 0 else 'FAIL'} lines={changed}")
