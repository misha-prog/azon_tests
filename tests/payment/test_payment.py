import pytest

from data.orders import OrdersData
from models.orders import OrderResponse, PaymentBriefResponse, PaymentResponse

pytestmark = [pytest.mark.payment]


class TestPayment:
    def test_check_bin(self, authenticated_user, api_manager):
        response = api_manager.payment_api.get_orders()

        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_success_card_transfer_order_to_status_paid(
        self, api_manager, authenticated_user, order
    ):
        response = api_manager.payment_api.pay_order(order.id, OrdersData.success_card())
        payment = PaymentResponse.model_validate(response.json())

        assert payment.status == "SUCCEEDED", (
            f"Статус заказа не успешен, а выдал нам - {response.text}"
        )
        assert payment.order_status == "PAID"

        response_order = api_manager.payment_api.get_order(order.id)
        paid_order = OrderResponse.model_validate(response_order.json())

        assert paid_order.status == "PAID", (
            "Заказ почему то не был успешно оплачен, "
            f"ответ получения заказа: {response_order.text}"
        )

    def test_payment_history_records_declined_and_succeeded_attempts(
        self, api_manager, authenticated_user, order
    ):
        api_manager.payment_api.pay_order(
            order.id, OrdersData.declined_card(), expected_status=402
        )
        successful_response = api_manager.payment_api.pay_order(
            order.id, OrdersData.success_card()
        )
        PaymentResponse.model_validate(successful_response.json())

        response = api_manager.payment_api.get_order_payments(order.id)
        payments = [
            PaymentBriefResponse.model_validate(payment) for payment in response.json()
        ]

        assert [payment.status for payment in payments] == ["DECLINED", "SUCCEEDED"]
        assert payments[0].decline_code == "card_declined"
        assert payments[1].decline_code is None


@pytest.mark.negative
class TestPaymentNegative:
    def test_invalid_card_decline_payment(self, api_manager, authenticated_user, order):
        response = api_manager.payment_api.pay_order(
            order.id, OrdersData.declined_card(), expected_status=402
        )

        assert response.json()["error"]["code"] == "PAYMENT_DECLINED", (
            f"Оплата волшебным образом прошла, либо выдало непонятную ошибку, "
            f"а тело ответа - {response.text}"
        )
        assert response.json()["error"]["details"][0]["decline_code"] == (
            "card_declined"
        )

    def test_repeat_payment_is_not_going_through(
        self, api_manager, authenticated_user, order
    ):
        api_manager.payment_api.pay_order(order.id, OrdersData.success_card())

        response = api_manager.payment_api.pay_order(
            order.id, OrdersData.success_card(), expected_status=409
        )

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

    @pytest.mark.roles
    def test_foreign_order_is_not_accessible(
        self, authenticated_user, api_manager, order, other_user
    ):
        response = other_user.payment_api.get_order(order.id, 404)

        assert response.json()["error"]["code"] == "ORDER_NOT_FOUND", (
            f"Ждали что заказ не найдется у другого пользователя, "
            f"но в итоге получили - {response.text}"
        )

    def test_empty_cart_cant_checkout(self, authenticated_user, api_manager):
        response = api_manager.payment_api.checkout(expected_status=400)

        assert response.json()["error"]["code"] == "CART_EMPTY", (
            f"Должна была выйти ошибка об оформлении пустой корзины, "
            f"но вышло следующее сообщение - {response.text}"
        )
