import uuid

import pytest

from tests.mocks.stubs import ProductStubs

pytestmark = pytest.mark.mock


def test_get_three_stubs_in_one(wiremock, mock_products_api):
    product_id = uuid.uuid4()
    stubs = ProductStubs.product_lifecycle(product_id)

    for stub in stubs:
        wiremock.add_stub(stub)

    resp_get = mock_products_api.get_product(product_id)

    resp_delete = mock_products_api.delete_product(product_id)

    resp_check = mock_products_api.get_product(product_id, 404)

    assert resp_get.status_code == 200
    assert resp_delete.status_code == 204
    assert resp_check.status_code == 404
    assert resp_check.json()["error"]["code"] == "PRODUCT_NOT_FOUND"
