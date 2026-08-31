import allure

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
