import uuid

import pytest
from requests.exceptions import ReadTimeout

from tests.mocks.stubs import ProductStubs

pytestmark = pytest.mark.mock


def test_server_error_is_503(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.bad_gateway(product_id))

    with pytest.raises(AssertionError) as error:
        mock_products_api.get_product(product_id)

    assert "ожидали статус 200, получили 503" in str(error.value)
    assert "GATEWAY_ERROR" in str(error.value)


def test_timeout_on_server(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.timeout_on_response(product_id))

    with pytest.raises(ReadTimeout):
        mock_products_api.get_product(product_id, timeout=2)
