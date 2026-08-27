from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page):
        self.page = page

        self.catalog_link = page.get_by_test_id("nav-catalog")
        self.cart_link = page.get_by_test_id("nav-cart")
        self.cart_count = page.get_by_test_id("cart-count")
        self.orders_link = page.get_by_test_id("nav-orders")
        self.profile_link = page.get_by_test_id("nav-profile")
        self.user_role = page.get_by_test_id("user-role")
        self.logout_button = page.get_by_test_id("logout-button")

        self.login_link = page.get_by_test_id("nav-login")
        self.register_link = page.get_by_test_id("nav-register")

    def go_to_cart(self):
        self.cart_link.click()

    def go_to_orders(self):
        self.orders_link.click()

    def go_to_catalog(self):
        self.catalog_link.click()

    def logout(self):
        self.logout_button.click()
