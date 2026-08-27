import pytest
from playwright.sync_api import expect

from config.hosts import FRONTEND_URL
from data.users import UserData
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

pytestmark = [pytest.mark.ui, pytest.mark.auth]


@pytest.mark.negative
def test_login_with_wrong_password(api_manager, page):
    user = UserData.registration_data()
    api_manager.auth_api.register_user(user)

    page.goto(f"{FRONTEND_URL}/login")
    page.get_by_test_id("email-input").fill(user.email)
    page.get_by_test_id("password-input").fill("abababababab")
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_test_id("login-error")).to_be_visible()
    expect(page.get_by_test_id("login-error")).to_have_text("Invalid email or password")


def test_registration_through_from_leads_to_login(page):
    user_data = UserData.registration_data()
    register_page = RegisterPage(page).open()

    register_page.register(user_data.full_name, user_data.email, user_data.password)

    login_page = LoginPage(page)
    expect(login_page.flash).to_have_text("Аккаунт создан — войдите")
    expect(login_page.form).to_be_visible()


def test_header_state_for_guest_and_buyer(page, ui_user):
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
