import allure
from decimal import Decimal

from pages.base_page import BasePage


class CartPage(BasePage):
    """Корзина: /cart."""

    url = "/cart"

    def __init__(self, page):
        super().__init__(page)

        self.table = page.get_by_test_id("cart-table")
        self.items = page.get_by_test_id("cart-item")
        self.total = page.get_by_test_id("cart-total")
        self.empty = page.get_by_test_id("cart-empty")

        self.clear_button = page.get_by_test_id("cart-clear")
        self.checkout_button = page.get_by_test_id("checkout-button")

    def item(self, name):
        """Строка корзины с нужным товаром."""
        return self.items.filter(has_text=name)

    def item_quantity(self, name):
        return self.item(name).get_by_test_id("cart-item-quantity")

    @allure.step("Меняем количество товара {name} на {quantity}")
    def set_quantity(self, name, quantity):
        row = self.item(name)
        self.item_quantity(name).fill(str(quantity))
        row.get_by_test_id("cart-item-update").click()

    @allure.step("Очищаем корзину")
    def clear(self):
        self.clear_button.click()

    @allure.step("Оформляем заказ")
    def checkout(self):
        self.checkout_button.click()

    @allure.step("Удаляем товар {name}")
    def remove(self, name):
        self.item(name).get_by_test_id("cart-item-remove").click()

    @allure.step("Сохраняем цену товара")
    def save_price(self, name):
        row = self.item(name)
        return row.get_by_test_id("cart-item-price")

    @staticmethod
    def _parse_price(text: str) -> Decimal:
        cleaned_text = (
            text.replace("Итого:", "")
            .replace("₽", "")
            .replace("\xa0", "")
            .replace(" ", "")
            .strip()
        )
        return Decimal(cleaned_text)

    @allure.step("Сохраняем цену товара")
    def item_price(self, name: str) -> Decimal:
        price_text = self.item(name).get_by_test_id(
            "cart-item-price"
        ).inner_text()

        return self._parse_price(price_text)

    @allure.step("Забираем итог со страницы")
    def total_price(self) -> Decimal:
        return self._parse_price(self.total.inner_text())