# Task contract: issue 2, delivered orders can be cancelled

**Goal:** Delivered orders must not be cancellable (issue #2).

**Context:** `AGENTS.md` (order state machine), `tests/unit/test_orders.py`

**In scope:** `app/modules/orders/service.py`, `tests/unit/test_orders.py`, `tests/integration/test_orders.py`

**Out of scope:** `alembic/`, `.github/`, `pyproject.toml`, any new dependency

**Acceptance:**
- A new unit test fails on the current code and passes after the fix.
- `POST /orders/{id}/cancel` on a delivered order returns 400.
- `python -m pytest tests/unit -q` passes.

**Stop and ask a human if:** the fix needs a schema change or a change in the payment module.

**Reviewer:** your second account
