import pytest

from utils.marks import requires_admin, requires_db

pytestmark = [pytest.mark.db, pytest.mark.payment, requires_db, requires_admin]


def test_checkout_saves_product_snapshot(created_order, created_product, db):
    items = db.payment.get_order_items(created_order["id"])

    assert len(items) == 1
    assert items[0]["product_id"] == created_product.id
    assert items[0]["product_name"] == created_product.name
    assert items[0]["unit_price"] == created_product.price
