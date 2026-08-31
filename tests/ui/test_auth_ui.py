import allure
import pytest
from playwright.sync_api import expect

from data.users import UserData
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.auth]


@allure.epic("Витрина AZON")
@allure.feature("Авторизация")
class TestAuthPositive:
    @allure.story("Вход")
    @allure.title("Зарегистрированный покупатель входит в аккаунт")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registered_buyer_can_login(self, page, ui_user):
        login_page = LoginPage(page).open()
        login_page.login(ui_user.email, ui_user.password)

        expect(login_page.header.profile_link).to_have_text(ui_user.email)

    @allure.story("Шапка сайта")
    @allure.title("Шапка меняется после входа и выхода покупателя")
    @allure.severity(allure.severity_level.NORMAL)
    def test_header_state_for_guest_and_buyer(self, page, ui_user):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.header.login_link).to_be_visible()
        expect(catalog_page.header.register_link).to_be_visible()

        LoginPage(page).open().login(ui_user.email, ui_user.password)
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.header.orders_link).to_be_visible()
        expect(catalog_page.header.cart_link).to_be_visible()
        expect(catalog_page.header.profile_link).to_have_text(ui_user.email)
        expect(catalog_page.header.user_role).to_have_text("USER")

        catalog_page.header.logout()

        expect(catalog_page.header.login_link).to_be_visible()
        expect(catalog_page.header.register_link).to_be_visible()

    @allure.story("Шапка сайта")
    @allure.title("Гостевая шапка меняется на пользовательскую после входа")
    @allure.severity(allure.severity_level.NORMAL)
    def test_default_header_swaps_to_user_after_login(self, page, ui_user):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.header.login_link).to_be_visible()
        expect(catalog_page.header.register_link).to_be_visible()

        LoginPage(page).open().login(ui_user.email, ui_user.password)

        expect(catalog_page.header.profile_link).to_be_visible()
        expect(catalog_page.header.profile_link).to_have_text(ui_user.email)
        expect(catalog_page.header.logout_button).to_be_visible()


@pytest.mark.negative
@allure.epic("Витрина AZON")
@allure.feature("Авторизация")
class TestAuthNegative:
    @allure.story("Ошибки входа")
    @allure.title("Вход с неправильным паролем отклоняется")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_with_wrong_password(self, api_manager, page):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)

        login_page = LoginPage(page).open()
        login_page.login(user.email, f"{user.password}x")

        expect(login_page.error).to_be_visible()
        expect(login_page.error).to_have_text("Invalid email or password")

    @allure.story("Ошибки входа")
    @allure.title("Ошибка неправильного пароля отображается в форме")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_failed_error_on_place(self, page, ui_user):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.header.login_link).to_be_visible()
        expect(catalog_page.header.register_link).to_be_visible()

        login_page = LoginPage(page).open()
        login_page.login(ui_user.email, f"{ui_user.password}x")

        expect(login_page.error).to_have_text("Invalid email or password")
