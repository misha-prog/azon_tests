import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.order_page import DECLINED_CARD, OrderPage
from pages.orders_page import OrdersPage

pytestmark = pytest.mark.ui


@allure.epic("Витрина AZON")
@allure.feature("Заказы и оплата")
class TestOrdersPositive:
    @allure.story("История заказов")
    @allure.title("Новый заказ появляется в списке заказов")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_new_order_appears_in_list(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")
        CartPage(logged_in_page).open().checkout()
        order_id = logged_in_page.url.rsplit("/", 1)[-1]

        orders_page = OrdersPage(logged_in_page).open()

        expect(orders_page.row(order_id)).to_be_visible()
        expect(orders_page.row_status(order_id)).to_have_text("AWAITING_PAYMENT")
    @allure.story("Статусы заказа")
    @allure.title("Новый заказ ожидает оплаты")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_in_awaiting_status(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()

        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        CartPage(logged_in_page).open().checkout()
        order_id = logged_in_page.url.rsplit("/", 1)[-1]

        orders_page = OrdersPage(logged_in_page).open()

        expect(orders_page.row(order_id)).to_be_visible()
        expect(orders_page.row_status(order_id)).to_have_text("AWAITING_PAYMENT")

    @pytest.mark.payment
    @allure.story("Оплата")
    @allure.title("Успешная оплата переводит заказ в статус PAID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_in_paid_status(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()

        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        CartPage(logged_in_page).open().checkout()
        order_id = logged_in_page.url.rsplit("/", 1)[-1]

        order_page = OrderPage(logged_in_page)
        expect(order_page.status).to_have_text("AWAITING_PAYMENT")

        order_page.pay()

        expect(order_page.status).to_have_text("PAID")

        orders_page = OrdersPage(logged_in_page).open()
        order_row = orders_page.row(order_id)

        expect(order_row).to_be_visible()
        expect(orders_page.row_status(order_id)).to_have_text("PAID")


@pytest.mark.negative
@allure.epic("Витрина AZON")
@allure.feature("Заказы и оплата")
class TestOrdersNegative:
    @pytest.mark.payment
    @allure.story("Оплата")
    @allure.title("Отказ банка оставляет заказ неоплаченным")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_declined_payment_keeps_order_unpaid(
        self, logged_in_page, created_product
    ):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)

        order_page.pay(card_number=DECLINED_CARD)

        expect(order_page.status).to_have_text("AWAITING_PAYMENT")
        expect(order_page.payments_table).to_be_visible()
        expect(order_page.payment_status).to_have_text("DECLINED")
        expect(order_page.payment_decline_code).to_have_text("card_declined")
