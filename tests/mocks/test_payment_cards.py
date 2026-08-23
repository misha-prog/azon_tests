import uuid

import pytest
from requests import ReadTimeout

from data.orders import OrdersData
from tests.mocks.stubs import PaymentStubs

pytestmark = [pytest.mark.mock, pytest.mark.payment]


def test_slow_card_payment(wiremock, mock_payment_api):
    order_id = uuid.uuid4()
    card_data = OrdersData.slow_card()

    wiremock.add_stub(PaymentStubs.get_response_of_slow_service(order_id))

    with pytest.raises(ReadTimeout):
        mock_payment_api.pay_order(order_id, card_data, timeout=2)
