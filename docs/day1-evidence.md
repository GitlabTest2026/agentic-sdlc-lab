# Day 1 Lab 1.3 evidence

## Repository changes

- The README's get-order example uses `GET /orders/1`, matching the orders router.
- Cancelling a delivered order raises `OrderOwnershipError` with the message `Cannot cancel a delivered order`; the cancel route maps this error to HTTP 400.
- Order-list status filtering is covered by a regression test for `GET /orders/?status=shipped`.

## Verification

- `python -m pytest tests/unit -q` - 91 passed.
- Focused order integration tests, using SQLite - 2 passed: status filtering and delivered-order cancellation.

This evidence records repository and test results only. It makes no claims about issue-tracker actions, external tool activity, or benchmark runs.
