from pages.base_page import BasePage


class OrdersPage(BasePage):
    url = "/orders"

    def __init__(self, page):
        super().__init__(page)

        self.table = page.get_by_test_id("orders-table")
        self.rows = page.get_by_test_id("order-row")
        self.empty = page.get_by_test_id("orders-empty")

    def row(self, order_id):
        return self.rows.filter(has_text=str(order_id)[:8])

    def open_first(self):
        self.rows.first.get_by_test_id("order-link").click()