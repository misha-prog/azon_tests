import pytest
from playwright.sync_api import expect

from config.hosts import FRONTEND_URL
from data.users import UserData

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