import re

import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.products]


@allure.epic("Витрина AZON")
@allure.feature("Каталог")
class TestCatalogPositive:
    @allure.story("Отображение каталога")
    @allure.title("Каталог показывает созданный товар")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_catalog_shows_products(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.title).to_have_text("Каталог")
        expect(catalog_page.total).to_contain_text("Найдено товаров")
        expect(catalog_page.card(created_product.name)).to_be_visible()

    @allure.story("Фильтрация")
    @allure.title("Фильтр категории показывает товар выбранной категории")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_filter_narrows_catalog(
        self, page, created_product, category
    ):
        catalog_page = CatalogPage(page).open()
        catalog_page.choose_category(category["name"])

        expect(catalog_page.selected_category).to_have_text(category["name"])
        expect(catalog_page.card(created_product.name)).to_be_visible()

    @allure.story("Сортировка")
    @allure.title("Товары сортируются по возрастанию цены")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_of_products_sorted_in_the_right_way(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.sort_by("По цене")
        prices = catalog_page.prices()
        assert prices == sorted(prices), (
            f"Цены должны быть отсортированы по возрастанию. "
            f"Получили: {prices}"
        )

    @allure.story("Пагинация")
    @allure.title("Из каталога можно перейти на вторую страницу")
    @allure.severity(allure.severity_level.NORMAL)
    def test_second_page_available(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.go_to_next_page()

        expect(page).to_have_url(re.compile(r".*page=2.*"))
        expect(catalog_page.page_link(2)).to_be_visible()

    @allure.story("Доступ гостя")
    @allure.title("Добавление товара гостем переводит на страницу входа")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_guest_add_to_cart_goes_to_login(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(page).to_have_url(re.compile(r"/login"))
        expect(LoginPage(page).form).to_be_visible()

    @allure.story("Поиск")
    @allure.title("Поиск находит созданный через API товар")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_finds_created_product(self, created_product, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.card(created_product.name)).to_be_visible()
        expect(catalog_page.cards).to_have_count(1)

    @allure.story("Фильтрация")
    @allure.title("Поиск и категория совместно фильтруют каталог")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_searched_product_with_filters_in_catalog(
        self, logged_in_page, created_product, category
    ):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.filter(created_product.name, category["name"])

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()
        expect(catalog_page.selected_category).to_have_text(category["name"])

    @allure.story("Добавление в корзину")
    @allure.title("Товар добавляется в корзину из каталога")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_product_in_cart(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()

        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.toast).to_have_text("Товар добавлен в корзину")
        expect(catalog_page.header.cart_count).to_have_text("1")


@pytest.mark.negative
@allure.epic("Витрина AZON")
@allure.feature("Каталог")
class TestCatalogNegative:
    @allure.story("Поиск")
    @allure.title("Поиск отсутствующего товара показывает пустое состояние")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_without_results_shows_empty_state(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.search("такого-товара-точно-нет-12345")

        expect(catalog_page.empty).to_be_visible()
        expect(catalog_page.cards).to_have_count(0)
