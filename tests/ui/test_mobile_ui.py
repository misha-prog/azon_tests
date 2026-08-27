import pytest
import re

from playwright.sync_api import expect
from config.hosts import FRONTEND_URL
from data.users import UserData
from pages.catalog_page import CatalogPage

pytestmark = [pytest.mark.ui, pytest.mark.mobile]

MOBILE_WIDTH = 390

def page_width(page):
    return page.evaluate(
        "() => ({scroll: document.documentElement.scrollWidth,"
        " client: document.documentElement.clientWidth})"
    )


def test_viewport_is_phone_sized(mobile_page):
    mobile_page.goto(FRONTEND_URL)

    assert mobile_page.viewport_size["width"] == MOBILE_WIDTH


def test_tap_on_add_to_cart_sends_guest_to_login(mobile_page):
    mobile_page.goto(FRONTEND_URL)


    mobile_page.get_by_test_id("product-card").first.get_by_test_id("add-to-cart").tap()

    expect(mobile_page).to_have_url(re.compile(r"/login"))
    expect(mobile_page.get_by_test_id("login-form")).to_be_visible()


"""
Тест не нужен поскольку доработали в более читабельную и короткую версию с удобствами
@pytest.mark.xfail(strict=True, reason="AZON-207: шапка авторизованного пользователя не помещается в 390 px")
def test_logged_in_catalog_has_no_side_scroll(mobile_page, api_manager):
    user = UserData.registration_data()
    api_manager.auth_api.register_user(user)

    mobile_page.goto(f"{FRONTEND_URL}/login")
    mobile_page.get_by_test_id("email-input").fill(user.email)
    mobile_page.get_by_test_id("password-input").fill(user.password)
    mobile_page.get_by_test_id("login-submit").click()
    expect(mobile_page.get_by_test_id("nav-profile")).to_have_text(user.email)

    mobile_page.goto(FRONTEND_URL)
    width = page_width(mobile_page)

    assert width["scroll"] <= width["client"], (
        f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
    )
"""

def test_catalog_is_single_column(mobile_page):
    mobile_page.goto(FRONTEND_URL)

    card = mobile_page.get_by_test_id("product-card").first.bounding_box()

    assert card["width"] > MOBILE_WIDTH * 0.9, (
        f"Карточка занимает {card['width']} px - на телефоне ожидали одну колонку во всю ширину"
    )


def test_guest_catalog_has_no_side_scroll(mobile_page):
    mobile_page.goto(FRONTEND_URL)

    width = page_width(mobile_page)

    assert width["scroll"] <= width["client"], (
        f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
    )


def test_search_on_phone_finds_product(mobile_page, created_product):
    mobile_page.goto(FRONTEND_URL)

    mobile_page.get_by_test_id("search-input").fill(created_product.name)
    mobile_page.get_by_test_id("apply-filters").click()

    cards = mobile_page.get_by_test_id("product-card")
    expect(cards).to_have_count(1)
    expect(cards.get_by_test_id("product-name")).to_have_text(created_product.name)


@pytest.mark.xfail(strict=True, reason="AZON-207: шапка авторизованного пользователя не помещается в 390 px")
def test_logged_in_catalog_has_no_side_scroll(logged_in_mobile_page):
    CatalogPage(logged_in_mobile_page).open()

    width = page_width(logged_in_mobile_page)

    assert width["scroll"] <= width["client"], (
        f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
    )