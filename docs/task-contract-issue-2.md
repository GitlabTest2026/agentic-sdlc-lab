# Task contract: issue 2 — delivered orders cannot be cancelled
**Goal:** Reject cancellation of delivered orders.
**Context:** `AGENTS.md` order state machine; `tests/unit/test_orders.py`.
**In scope:** `app/modules/orders/service.py`, `tests/unit/test_orders.py`, `tests/integration/test_orders.py`.
**Out of scope:** `alembic/`, `.github/`, `pyproject.toml`, new dependencies.
**Acceptance:** Add a unit test that fails before the fix and passes after.
**Acceptance:** `POST /orders/{id}/cancel` returns HTTP 400 for delivered orders.
**Validation:** `$env:AUTH_JWT_SECRET_KEY="test-secret-key-for-local-dev-only"; python -m pytest tests/unit -q` passes.
**Stop and ask:** If the fix requires a schema or payment-module change.
**Reviewer:** your second account.
