import allure
import pytest
from playwright.sync_api import expect

from data.users import UserData
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.order_page import OrderPage

pytestmark = [pytest.mark.ui, pytest.mark.payment]


def login(page, user):
    login_page = LoginPage(page).open()
    login_page.login(user.email, user.password)
    expect(login_page.header.profile_link).to_have_text(user.email)


def put_product_in_cart(page, product):
    catalog_page = CatalogPage(page).open()
    catalog_page.search(product.name)
    catalog_page.add_to_cart(product.name)
    expect(catalog_page.header.cart_count).to_have_text("1")


@allure.epic("Витрина AZON")
@allure.feature("Корзина")
class TestCartPositive:
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
    @allure.title("Кнопка В корзину показывает тост и обновляет бейдж")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_shows_toast_and_updates_badges(
        self, page, api_manager, created_product
    ):
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

        cart_page = CartPage(page).open()
        one_item_total = cart_page.total.inner_text()

        cart_page.set_quantity(created_product.name, 3)

        expect(cart_page.item_quantity(created_product.name)).to_have_value("3")
        expect(cart_page.total).not_to_have_text(one_item_total)

    @allure.story("Содержимое корзины")
    @allure.title("Пустая корзина показывает заглушку")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_cart_shows_empty_state(self, page, api_manager):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)
        login(page, user)

        cart_page = CartPage(page).open()

        expect(cart_page.empty).to_be_visible()
        expect(cart_page.checkout_button).to_have_count(0)

    @allure.story("Содержимое корзины")
    @allure.title("Удаление товара оставляет корзину пустой")
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

    @allure.story("Заказы")
    @allure.title("Созданный заказ можно отменить")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_can_be_cancelled(self, logged_in_page, created_product):
        put_product_in_cart(logged_in_page, created_product)

        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)
        order_page.cancel()

        expect(order_page.flash).to_have_text("Заказ отменён")
        expect(order_page.status).to_have_text("CANCELLED")

    @allure.story("Содержимое корзины")
    @allure.title("Количество товара и итоговая сумма пересчитываются")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_count_in_cart_can_be_edited(self, created_product, logged_in_page):
        catalog_page = CatalogPage(logged_in_page).open()

        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        cart_page = CartPage(logged_in_page).open()
        quantity_input = cart_page.item_quantity(created_product.name)
        initial_total = cart_page.total.inner_text()

        cart_page.set_quantity(created_product.name, 10)

        expect(quantity_input).to_have_value("10")
        expect(cart_page.total).not_to_have_text(initial_total)
