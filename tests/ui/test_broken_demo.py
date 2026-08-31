import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.ui


@allure.epic("Витрина AZON")
@allure.feature("Каталог")
class TestCatalogTitlePositive:
    @allure.story("Заголовок страницы")
    @allure.title("Каталог отображает правильный заголовок")
    @allure.severity(allure.severity_level.NORMAL)
    def test_catalog_title_is_visible(self, page):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.title).to_have_text("Каталог")
