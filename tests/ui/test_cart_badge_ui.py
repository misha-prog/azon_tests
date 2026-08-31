import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.ui


@allure.epic("Витрина AZON")
@allure.feature("Корзина")
class TestCartBadgePositive:
    @allure.story("Бейдж корзины")
    @allure.title("Бейдж пустой корзины показывает ноль")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_badge_shows_zero(self, logged_in_page):
        catalog_page = CatalogPage(logged_in_page).open()

        expect(catalog_page.header.cart_count).to_have_text("0")

    @allure.story("Содержимое корзины")
    @allure.title("Добавленный товар отображается в корзине")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_is_in_cart(self, logged_in_page, created_product) -> None:
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(catalog_page.header.cart_count).to_have_text("1")
        catalog_page.header.go_to_cart()

        cart_page = CartPage(logged_in_page)
        expect(cart_page.item(created_product.name)).to_be_visible()
