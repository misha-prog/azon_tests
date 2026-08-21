from config.hosts import PAYMENT_URL
from requester.custom_requester import CustomRequester


class PaymentAPI(CustomRequester):
    """Класс для получения инфорации о корзине"""
    ORDERS_ENDPOINT = "/api/v1/orders"

    def __init__(self, session, base_url=PAYMENT_URL):
        super().__init__(session, base_url)

    def get_orders(self, params=None, expected_status=200):
        return self.send_request("GET", self.ORDERS_ENDPOINT, params=params, expected_status=expected_status)

    def checkout(self, expected_status=201):
        return self.send_request("POST", f"{self.ORDERS_ENDPOINT}/checkout", json={}, expected_status=expected_status)

    def get_order(self, order_id, expected_status=200):
        return self.send_request("GET", f"{self.ORDERS_ENDPOINT}/{order_id}", json={}, expected_status=expected_status)

    def pay_order(self, order_id, card_data,expected_status=201):
        return self.send_request("POST", f"{self.ORDERS_ENDPOINT}/{order_id}/pay", json=card_data, expected_status=expected_status)

    def cancel_order(self, order_id, expected_status=200):
        return self.send_request("POST", f"{self.ORDERS_ENDPOINT}/{order_id}/cancel", expected_status=expected_status)

    def get_order_payments(self, order_id, expected_status=200):
        return self.send_request("GET", f"{self.ORDERS_ENDPOINT}/{order_id}/payments", expected_status=expected_status)
