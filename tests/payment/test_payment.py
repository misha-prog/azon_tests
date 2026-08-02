from requester.custom_requester import CustomRequester
import pytest


class TestPayment:

    def test_check_bin(self, authorized_user, api_manager):
        response = api_manager.payment_api.get_orders()

        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    @pytest.mark.parametrize("client_name", ["auth_api", "products_api", "payment_api"])
    def test_health(self, api_manager, client_name):
        client = getattr(api_manager, client_name)