import uuid
from decimal import Decimal

import pytest

from models.products import ProductsPage
from tests.mocks.stubs import ProductStubs

pytestmark = [pytest.mark.mock]


def test_server_error_message_is_readable(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.product_not_found(product_id))

    with pytest.raises(AssertionError) as error:
        mock_products_api.get_product(product_id)

    assert "ожидали статус 200, получили 404" in str(error.value)
    assert "PRODUCT_NOT_FOUND" in str(error.value)


def test_stub_with_fake_products(wiremock, mock_products_api):
    wiremock.add_stub(ProductStubs.product_page_and_size())

    response = mock_products_api.get_products(params={"size": 2, "page": 1})

    products = ProductsPage.model_validate(response.json())

    assert products.total == 2
    assert len(products.items) == 2
    assert products.items[1].price == Decimal("1000")
