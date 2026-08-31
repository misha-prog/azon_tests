import re

import allure

from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Главная страница витрины: каталог товаров с фильтрами и постраничной выдачей."""

    url = "/"

    def __init__(self, page):
        super().__init__(page)

        self.grid = page.get_by_test_id("catalog-grid")
        self.cards = page.get_by_test_id("product-card")
        self.total = page.get_by_test_id("catalog-total")
        self.empty = page.get_by_test_id("catalog-empty")

        self.search_input = page.get_by_test_id("search-input")
        self.category_select = page.get_by_test_id("category-select")
        self.selected_category = self.category_select.locator("option:checked")
        self.sort_select = page.get_by_test_id("sort-select")
        self.order_select = page.get_by_test_id("order-select")
        self.apply_button = page.get_by_test_id("apply-filters")
        self.product_prices = self.cards.get_by_test_id("product-price")

        self.pagination = page.get_by_test_id("pagination")
        self.next_page_button = page.get_by_test_id("pagination-next")

    def card(self, name):
        """Карточка нужного товара: ищем среди всех карточек ту, где есть это название."""
        exact_name = self.page.get_by_test_id("product-name").filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )
        return self.cards.filter(has=exact_name)

    @allure.step("Ищем товар {text}")
    def search(self, text):
        self.search_input.fill(text)
        self.apply_button.click()

    @allure.step("Фильтруем каталог по запросу {text} и категории {category}")
    def filter(self, text, category):
        self.search_input.fill(text)
        self.category_select.select_option(label=category)
        self.apply_button.click()

    @allure.step("Выбираем категорию {name}")
    def choose_category(self, name):
        self.category_select.select_option(label=name)
        self.apply_button.click()

    @allure.step("Сортируем по {label} и по {order}")
    def sort_by(self, label, order="По возрастанию"):
        self.sort_select.select_option(label=label)
        self.order_select.select_option(label=order)
        self.apply_button.click()

    @allure.step("Добавляем товар {name} в корзину")
    def add_to_cart(self, name):
        self.card(name).get_by_test_id("add-to-cart").click()

    @allure.step("Добавляем товар {name} в корзину касанием")
    def tap_add_to_cart(self, name):
        self.card(name).get_by_test_id("add-to-cart").tap()

    @allure.step("Открываем товар {name}")
    def open_product(self, name):
        self.card(name).get_by_test_id("product-name").click()

    @allure.step("Переходим на следующую страницу каталога")
    def go_to_next_page(self):
        self.next_page_button.click()

    def page_link(self, number):
        return self.page.get_by_role("link", name=str(number), exact=True)

    def first_card_box(self):
        return self.cards.first.bounding_box()

    @allure.step("Получаем цены товаров из каталога")
    def prices(self):
        """Цены всех карточек на странице числами: «58 171.00 ₽» -> 58171.0."""
        return [
            float(text.replace("₽", "").replace("\xa0", "").replace(" ", ""))
            for text in self.product_prices.all_inner_texts()
        ]
