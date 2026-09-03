import re

import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.mobile]

MOBILE_WIDTH = 390


def page_width(page):
    return page.evaluate(
        "() => ({scroll: document.documentElement.scrollWidth,"
        " client: document.documentElement.clientWidth})"
    )


@allure.epic("Витрина AZON")
@allure.feature("Мобильная версия")
class TestMobilePositive:
    @allure.story("Эмуляция устройства")
    @allure.title("Мобильная страница открывается с шириной телефона")
    @allure.severity(allure.severity_level.NORMAL)
    def test_viewport_is_phone_sized(self, mobile_page):
        CatalogPage(mobile_page).open()

        assert mobile_page.viewport_size["width"] == MOBILE_WIDTH


    @allure.story("Доступ гостя")
    @allure.title("Добавление товара гостем на телефоне открывает вход")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tap_on_add_to_cart_sends_guest_to_login(
        self, mobile_page, created_product
    ):
        catalog_page = CatalogPage(mobile_page).open()
        catalog_page.search(created_product.name)
        catalog_page.tap_add_to_cart(created_product.name)

        expect(mobile_page).to_have_url(re.compile(r"/login"))
        expect(LoginPage(mobile_page).form).to_be_visible()


    @allure.story("Адаптивная вёрстка")
    @allure.title("Каталог на телефоне помещается в одну колонку")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_mobile_catalog_is_single_column_without_side_scroll(
        self, mobile_page, created_product
    ):
        catalog_page = CatalogPage(mobile_page).open()
        catalog_page.search(created_product.name)

        card = catalog_page.first_card_box()
        width = page_width(mobile_page)

        assert card["width"] > MOBILE_WIDTH * 0.9, (
            f"Карточка занимает {card['width']} px - "
            "на телефоне ожидали одну колонку во всю ширину"
        )
        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px "
            f"против {width['client']} px"
        )


    @allure.story("Поиск")
    @allure.title("Поиск товара работает на телефоне")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_on_phone_finds_product(
        self, mobile_page, created_product
    ):
        catalog_page = CatalogPage(mobile_page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()


@allure.epic("Витрина AZON")
@allure.feature("Мобильная версия")
class TestMobileKnownIssues:

    @allure.issue(
        "AZON-207",
        "Шапка авторизованного пользователя не помещается на мобильном экране",
    )
    @pytest.mark.xfail(
        strict=True,
        reason="AZON-207: шапка авторизованного пользователя не помещается в 390 px",
    )
    @allure.story("Известные дефекты")
    @allure.title("Авторизованная шапка не помещается на мобильном экране")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logged_in_catalog_has_no_side_scroll(
        self, logged_in_mobile_page
    ):
        CatalogPage(logged_in_mobile_page).open()

        width = page_width(logged_in_mobile_page)

        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px "
            f"против {width['client']} px"
        )
