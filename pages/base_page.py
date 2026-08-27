from playwright.sync_api import Page

from config.hosts import FRONTEND_URL
from pages.components.header import Header


class BasePage:
    url = "/"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)

        # два вида сообщений: flash приходит с сервера, toast рисует JS
        self.flash = page.get_by_test_id("flash-message")
        self.toast = page.get_by_test_id("toast")

        self.title = page.get_by_test_id("page-title")

    def open(self):
        self.page.goto(f"{FRONTEND_URL}{self.url}")
        return self
