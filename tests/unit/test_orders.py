from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import pytest

from app.modules.orders import service, repository, models, schemas
from app.modules.orders.exceptions import OrderOwnershipError
from app.modules.orders.service import OrderStateMachine, InvalidOrderTransition


def _make_mock_repo(order=None):
    repo = MagicMock(spec=repository.OrderRepository)
    repo._db = MagicMock()
    repo.get_order.return_value = order
    return repo


def _make_db():
    db = MagicMock()
    return db


def _make_order(item="widget", status="received"):
    order = MagicMock(spec=models.Order)
    order.id = 1
    order.item = item
    order.status = status
    order.delivered_at = None
    return order


def test_create_order():
    repo = _make_mock_repo()
    result = service.create_order(repo, 1, "laptop")
    repo.create_order.assert_called_once_with(1, "laptop")
    assert result == repo.create_order.return_value


def test_get_order():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    result = service.get_order(repo, 1)
    assert result == order


def test_get_order_not_found():
    repo = _make_mock_repo(order=None)
    try:
        service.get_order(repo, 999)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Order not found"


def test_list_orders():
    repo = _make_mock_repo()
    repo.list_orders.return_value = ([_make_order("a"), _make_order("b")], 2)
    result, total = service.list_orders(repo)
    assert len(result) == 2
    assert result[0].item == "a"
    assert result[1].item == "b"
    assert total == 2


def test_list_orders_passes_status_filter():
    repo = _make_mock_repo()
    repo.list_orders.return_value = ([], 0)

    service.list_orders(repo, user_id=1, status=models.OrderStatus.SHIPPED)

    repo.list_orders.assert_called_once_with(
        user_id=1,
        status=models.OrderStatus.SHIPPED,
        search=None,
        page=1,
        page_size=20,
    )


def test_update_order_status():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    db = _make_db()
    result = service.update_order(db, repo, 1, status="processing")
    assert result.status == "processing"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(order)


def test_update_order_item():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    db = _make_db()
    result = service.update_order(db, repo, 1, item="new_item")
    assert result.item == "new_item"
    assert result.status == "received"


def test_update_order_not_found():
    repo = _make_mock_repo(order=None)
    db = _make_db()
    try:
        service.update_order(db, repo, 999, status="shipped")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Order not found"


def test_delete_order():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    db = _make_db()
    service.delete_order(db, repo, 1)
    repo.delete_order.assert_called_once_with(1)
    db.commit.assert_called_once()


def test_delete_order_not_found():
    repo = _make_mock_repo(order=None)
    db = _make_db()
    try:
        service.delete_order(db, repo, 999)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Order not found"


# ── FSM Unit Tests ──────────────────────────────────────────────────────────

VALID_TRANSITIONS = [
    (models.OrderStatus.RECEIVED, models.OrderStatus.PROCESSING),
    (models.OrderStatus.RECEIVED, models.OrderStatus.CANCELLED),
    (models.OrderStatus.PROCESSING, models.OrderStatus.FULFILLED),
    (models.OrderStatus.PROCESSING, models.OrderStatus.CANCELLED),
    (models.OrderStatus.FULFILLED, models.OrderStatus.SHIPPED),
    (models.OrderStatus.FULFILLED, models.OrderStatus.CANCELLED),
    (models.OrderStatus.SHIPPED, models.OrderStatus.DELIVERED),
]

INVALID_TRANSITIONS = [
    (models.OrderStatus.RECEIVED, models.OrderStatus.FULFILLED),
    (models.OrderStatus.RECEIVED, models.OrderStatus.SHIPPED),
    (models.OrderStatus.RECEIVED, models.OrderStatus.DELIVERED),
    (models.OrderStatus.PROCESSING, models.OrderStatus.SHIPPED),
    (models.OrderStatus.PROCESSING, models.OrderStatus.DELIVERED),
    (models.OrderStatus.FULFILLED, models.OrderStatus.DELIVERED),
    (models.OrderStatus.FULFILLED, models.OrderStatus.RECEIVED),
    (models.OrderStatus.SHIPPED, models.OrderStatus.PROCESSING),
    (models.OrderStatus.SHIPPED, models.OrderStatus.CANCELLED),
    (models.OrderStatus.DELIVERED, models.OrderStatus.PROCESSING),
    (models.OrderStatus.DELIVERED, models.OrderStatus.DELIVERED),
    (models.OrderStatus.CANCELLED, models.OrderStatus.PROCESSING),
    (models.OrderStatus.CANCELLED, models.OrderStatus.CANCELLED),
]


@pytest.mark.parametrize("current, target", VALID_TRANSITIONS)
def test_fsm_valid_transitions(current, target):
    OrderStateMachine.validate_transition(current, target)


@pytest.mark.parametrize("current, target", INVALID_TRANSITIONS)
def test_fsm_invalid_transitions(current, target):
    with pytest.raises(InvalidOrderTransition):
        OrderStateMachine.validate_transition(current, target)


def test_fsm_unknown_current_status():
    with pytest.raises(InvalidOrderTransition):
        OrderStateMachine.validate_transition("unknown", models.OrderStatus.PROCESSING)


def test_fsm_unknown_target_status():
    with pytest.raises(InvalidOrderTransition):
        OrderStateMachine.validate_transition(models.OrderStatus.RECEIVED, "unknown")


def test_delivered_status_only_transitions_to_returned():
    assert OrderStateMachine.TRANSITIONS[models.OrderStatus.DELIVERED] == [
        models.OrderStatus.RETURNED,
    ]


def test_fsm_delivered_can_transition_to_returned():
    OrderStateMachine.validate_transition(
        models.OrderStatus.DELIVERED,
        models.OrderStatus.RETURNED,
        delivered_at=datetime.now(timezone.utc),
    )


def test_returned_status_is_terminal():
    assert OrderStateMachine.TRANSITIONS[models.OrderStatus.RETURNED] == []
    assert OrderStateMachine.is_terminal(models.OrderStatus.RETURNED)


# ── Service Layer FSM Integration Tests ─────────────────────────────────────


def test_cancel_order_delivered_raises_order_ownership_error():
    order = _make_order(status=models.OrderStatus.DELIVERED)
    repo = _make_mock_repo(order=order)
    db = _make_db()

    with pytest.raises(
        OrderOwnershipError, match="Cannot cancel a delivered order"
    ):
        service.cancel_order(db, repo, 1)

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_order_invalid_status_transition():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    db = _make_db()
    with pytest.raises(InvalidOrderTransition):
        service.update_order(db, repo, 1, status="delivered")
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_order_valid_status_transition():
    order = _make_order()
    repo = _make_mock_repo(order=order)
    db = _make_db()
    result = service.update_order(db, repo, 1, status="processing")
    assert result.status == "processing"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(order)


def test_update_order_return_without_delivery_timestamp():
    order = _make_order(status=models.OrderStatus.DELIVERED)
    repo = _make_mock_repo(order=order)
    db = _make_db()

    with pytest.raises(InvalidOrderTransition, match="delivery date"):
        service.update_order(db, repo, 1, status=models.OrderStatus.RETURNED)

    db.commit.assert_not_called()


def test_update_order_delivery_transition_sets_timestamp(monkeypatch):
    order = _make_order(status=models.OrderStatus.SHIPPED)
    repo = _make_mock_repo(order=order)
    db = _make_db()
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(service, "_utc_now", lambda: now)

    result = service.update_order(
        db, repo, 1, status=models.OrderStatus.DELIVERED
    )

    assert result.status == models.OrderStatus.DELIVERED
    assert result.delivered_at == now


def test_update_order_return_within_window_is_allowed(monkeypatch):
    order = _make_order(status=models.OrderStatus.DELIVERED)
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    order.delivered_at = now - timedelta(days=1)
    repo = _make_mock_repo(order=order)
    db = _make_db()
    monkeypatch.setattr(service, "_utc_now", lambda: now)

    result = service.update_order(
        db, repo, 1, status=models.OrderStatus.RETURNED
    )

    assert result.status == models.OrderStatus.RETURNED
    db.commit.assert_called_once()


def test_update_order_return_at_30_day_boundary_is_allowed(monkeypatch):
    order = _make_order(status=models.OrderStatus.DELIVERED)
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    order.delivered_at = now - timedelta(days=30)
    repo = _make_mock_repo(order=order)
    db = _make_db()
    monkeypatch.setattr(service, "_utc_now", lambda: now)

    service.update_order(db, repo, 1, status=models.OrderStatus.RETURNED)

    db.commit.assert_called_once()


def test_update_order_return_after_window_is_rejected(monkeypatch):
    order = _make_order(status=models.OrderStatus.DELIVERED)
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    order.delivered_at = now - timedelta(days=30, seconds=1)
    repo = _make_mock_repo(order=order)
    db = _make_db()
    monkeypatch.setattr(service, "_utc_now", lambda: now)

    with pytest.raises(InvalidOrderTransition, match="30-day return window"):
        service.update_order(
            db, repo, 1, status=models.OrderStatus.RETURNED
        )

    db.commit.assert_not_called()


def test_order_update_rejects_client_delivery_timestamp():
    with pytest.raises(ValueError):
        schemas.OrderUpdate.model_validate(
            {"delivered_at": "2026-10-28T12:00:00Z"}
        )
