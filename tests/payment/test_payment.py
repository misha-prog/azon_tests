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

        assert response.json()["status"] == "SUCCEEDED", (
            f"Статус заказа не успешен, "
            f"а выдал нам - {response.text}"
        )

        response_order = api_manager.payment_api.get_order(order.id)

        assert response_order.json()["status"] == "PAID", (
            f"Заказ почему то не был успешно оплачен, "
            f"а вот сам ответ получения заказа - {response_order.text}"
        )

class TestPaymentNegative:

    def test_invalid_card_decline_payment(self, api_manager, authenticated_user, order):
        response = api_manager.payment_api.pay_order(order.id, OrdersData.declined_card(), expected_status=402)

        assert response.json()["error"]["code"] == "PAYMENT_DECLINED", (
            f"Оплата волшебным образом прошла, либо выдало непонятную ошибку, "
            f"а тело ответа - {response.text}"
        )

    def test_repeat_payment_is_not_going_through(self, api_manager, authenticated_user, order):
        api_manager.payment_api.pay_order(order.id, OrdersData.success_card())

        response = api_manager.payment_api.pay_order(order.id, OrdersData.success_card(), expected_status=409)

        assert response.json()["error"]["code"] == "ORDER_NOT_PAYABLE", (
            f"Должна была вылететь ошибка о том что заказ нельзя оплатить, "
            f"поскольку он уже оплачен и выдало - {response.text}"
        )

    def test_refund_paid_order(self, api_manager, authenticated_user, order):
        api_manager.payment_api.pay_order(order.id, OrdersData.success_card())

        response = api_manager.payment_api.cancel_order(order.id, expected_status=409)

        assert response.json()["error"]["code"] == "INVALID_ORDER_STATUS", (
            f"Тут должна была быть ошибка об невалидном статусе заказа, "
            f"но получили следующее - {response.text}"
        )