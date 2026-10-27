#!/usr/bin/env bash
# Instructor: run once in the imported base repo. Creates the lab-start branch with the seeded problems.
set -euo pipefail
git checkout -b lab-start
python3 - <<'PY'
import re, pathlib
# Seed 1: remove the DELIVERED guard from cancel_order (no existing test covers it)
p = pathlib.Path("app/modules/orders/service.py"); s = p.read_text()
guard = '    if order.status == models.OrderStatus.DELIVERED:\n        raise OrderOwnershipError("Cannot cancel a delivered order")\n'
assert guard in s; p.write_text(s.replace(guard, ""))
# Seed 2: wrong route in the README example and the same mistake in AGENTS.md
r = pathlib.Path("README.md"); t = r.read_text()
assert "curl http://localhost:8000/orders/1" in t
r.write_text(t.replace("curl http://localhost:8000/orders/1", "curl http://localhost:8000/order/1"))
a = pathlib.Path("AGENTS.md"); a.write_text(a.read_text() + "\n## Example\n\n`curl http://localhost:8000/order/1` fetches one order.\n")
PY
git add -A && git commit -qm "lab: seed bug and wrong example"
echo "Now copy the kit files over the repo, commit, and make lab-start the default branch."
