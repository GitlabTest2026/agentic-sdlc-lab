#!/usr/bin/env bash
# Readiness check. Paste the output into the readiness issue.
set -u
ok(){ printf '  [ok]   %s\n' "$1"; }; bad(){ printf '  [FAIL] %s\n' "$1"; }
python3 --version | grep -q "3.1[2-9]" && ok "python >= 3.12" || bad "python >= 3.12"
gh auth status >/dev/null 2>&1 && ok "gh authenticated" || bad "gh not authenticated (run: gh auth login)"
docker info >/dev/null 2>&1 && ok "docker available (needed only for integration tests)" || bad "docker not available"
AUTH_JWT_SECRET_KEY=x python3 -m pytest tests/unit -q 2>&1 | tail -1 | grep -q passed && ok "unit tests pass" || bad "unit tests"
python3 -c "import mcp" 2>/dev/null && ok "mcp sdk installed" || bad "mcp sdk missing (pip install -r lab_mcp/requirements.txt)"
