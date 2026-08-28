import pytest
import allure
from playwright.sync_api import expect

from models.orders import OrdersPage
from pages import catalog_page
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from config.hosts import FRONTEND_URL
from data.users import UserData
from pages.order_page import OrderPage

pytestmark = [pytest.mark.ui, pytest.mark.payment]


def login(page, user):
    page.goto(f"{FRONTEND_URL}/login")
    page.get_by_test_id("email-input").fill(user.email)
    page.get_by_test_id("password-input").fill(user.password)
    page.get_by_test_id("login-submit").click()
    expect(page.get_by_test_id("nav-profile")).to_have_text(user.email)

def put_product_in_cart(page, product):
    catalog_page = CatalogPage(page).open()
    catalog_page.search(product.name)
    catalog_page.add_to_cart(product.name)
    expect(catalog_page.header.cart_count).to_have_text("1")

@allure.epic("Витрина AZON")
@allure.feature("Корзина")
class TestCartUI:

    @allure.story("Содержимое корзины")
    @allure.title("В корзине виден только что добавленный товар")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_shows_added_product(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        catalog_page.header.go_to_cart()

        cart_page = CartPage(logged_in_page)
        expect(cart_page.items).to_have_count(1)
        expect(cart_page.item(created_product.name)).to_be_visible()

    @allure.story("Добавление товара")
    @allure.title("Кнопка <В корзину> показывает тост и обновляет бейдж")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_shows_toast_and_updates_badges(self, page, api_manager, created_product):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)
        login(page, user)

        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(catalog_page.toast).to_have_text("Товар добавлен в корзину")
        expect(catalog_page.header.cart_count).to_have_text("1")

    @allure.story("Содержимое корзины")
    @allure.title("Смена количества пересчитывает итог")
    @allure.severity(allure.severity_level.NORMAL)
    def test_quantity_can_be_edited(self, page, created_product, api_manager):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)
        login(page, user)
        put_product_in_cart(page, created_product)

        page.get_by_test_id("nav-cart").click()
        row = page.get_by_test_id("cart-item").filter(has_text=created_product.name)
        one_item_total=page.get_by_test_id("cart-total").inner_text()

        row.get_by_test_id("cart-item-quantity").fill("3")
        row.get_by_test_id("cart-item-update").click()

        expect(row.get_by_test_id("cart-item-quantity")).to_have_value("3")
        assert page.get_by_test_id("cart-total").inner_text() != one_item_total

    @allure.story("Содержимое корзины")
    @allure.title("Пустая корзина показывает заглушку")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_cart_shows_empty_state(self, page, api_manager):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)
        login(page, user)

        page.goto(f"{FRONTEND_URL}/cart")

        expect(page.get_by_test_id("cart-empty")).to_be_visible()
        expect(page.get_by_test_id("checkout-button")).to_have_count(0)

    @allure.story("Содержимое корзины")
    @allure.title("Очистка корзины оставляет корзину пустой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_removed_product_leaves_cart_empty(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(catalog_page.header.cart_count).to_have_text("1")

        cart_page = CartPage(logged_in_page).open()
        expect(cart_page.item(created_product.name)).to_be_visible()

        cart_page.remove(created_product.name)
        expect(cart_page.empty).to_be_visible()
        expect(cart_page.items).to_have_count(0)

    @allure.story("Фичи с заказом")
    @allure.title("Заказа может быть отменен")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_can_be_cancelled(self, logged_in_page, created_product, page):
        put_product_in_cart(logged_in_page, created_product)

        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)
        order_page.cancel()

        expect(order_page.flash).to_have_text("Заказ отменён")
        expect(order_page.status).to_have_text("CANCELLED")
