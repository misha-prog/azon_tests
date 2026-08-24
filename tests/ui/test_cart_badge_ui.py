from config.hosts import FRONTEND_URL
from data.users import UserData
from playwright.sync_api import expect


def test_cart_badge_shows_zero(page, api_manager):
    user = UserData.registration_data()
    api_manager.auth_api.register_user(user)

    page.goto(f"{FRONTEND_URL}/login")
    page.get_by_test_id("email-input").fill(user.email)
    page.get_by_test_id("password-input").fill(user.password)
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_test_id("cart-count")).to_have_text("0")
    assert False, "Проверяем сохранение trace"
