from config.hosts import PAYMENT_URL
from requester.custom_requester import CustomRequester


class PaymentAPI(CustomRequester):
    """Класс для получения инфорации о корзине"""
    ORDERS_ENDPOINT = "/api/v1/orders"

    def __init__(self, session):
        super().__init__(session, base_url=PAYMENT_URL)

    def get_orders(self, params=None, expected_status=200):
        return self.send_request("GET", self.ORDERS_ENDPOINT, params=params, expected_status=expected_status)

    def checkout(self, expected_status=201):
        return self.send_request("POST", f"{self.ORDERS_ENDPOINT}/checkout", json={}, expected_status=expected_status)