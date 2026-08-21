import pytest

from data.orders import OrdersData

class TestPayment:

    def test_check_bin(self, authenticated_user, api_manager):
        response = api_manager.payment_api.get_orders()

        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    @pytest.mark.parametrize("client_name", ["auth_api", "products_api", "payment_api"])
    def test_health(self, api_manager, client_name):
        client = getattr(api_manager, client_name)

    def test_success_card_transfer_order_to_status_paid(self, api_manager, authenticated_user, order):
        response = api_manager.payment_api.pay_order(order.id, OrdersData.success_card())

        assert response.json()["status"] == "SUCCEEDED"

        response_order = api_manager.payment_api.get_order(order.id)

        assert response_order.json()["status"] == "PAID"