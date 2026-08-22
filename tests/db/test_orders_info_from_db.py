from decimal import Decimal

import pytest

pytestmark = [pytest.mark.db, pytest.mark.payment]

def test_primary_price_and_name_of_product_in_db(api_manager, db, authenticated_user, created_product):
    product_price = created_product.price
    product_name = created_product.name
    product = {
        "product_id": str(created_product.id),
        "quantity": 1,
    }
    api_manager.cart_api.add_item(product)

    created_product.price = Decimal("1")
    created_product.name = "abc"

    response = db.product.get_product(created_product.id)

    assert response["price"] == product_price
    assert response["name"] == product_name