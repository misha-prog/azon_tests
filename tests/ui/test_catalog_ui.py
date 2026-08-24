import pytest
from playwright.sync_api import expect
from decimal import Decimal

from config.hosts import FRONTEND_URL

pytestmark = [pytest.mark.ui, pytest.mark.products]


def parse_price(text: str) -> Decimal:
    cleaned = (
        text.replace("\xa0", "")
        .replace(" ", "")
        .replace("₽", "")
        .strip()
    )
    return Decimal(cleaned)


def test_catalog_shows_products(page):
    page.goto(FRONTEND_URL)

    expect(page.get_by_test_id("page-title")).to_have_text("Каталог")
    expect(page.get_by_test_id("catalog-total")).to_contain_text("Найдено товаров")
    assert page.get_by_test_id("product-card").count() > 0, "На витрине не нашлось ни одного товара"


@pytest.mark.negative
def test_search_without_results(page):
    page.goto(FRONTEND_URL)

    page.get_by_test_id("search-input").fill("fdsgb63564xb6")
    page.get_by_test_id("apply-filters").click()
    expect(page.get_by_test_id("catalog-empty")).to_be_visible()
    expect(page.get_by_test_id("product-card")).to_have_count(0)


def test_category_filter_narrows_catalog(page):
    page.goto(FRONTEND_URL)

    count = page.get_by_test_id("catalog-total")

    page.get_by_test_id("category-select").select_option("Книги")
    page.get_by_test_id("apply-filters").click()

    expect(page.get_by_test_id("category-select").locator("option:checked")).to_have_text("Книги")
    assert page.get_by_test_id("catalog-total").inner_text() != count


def test_list_of_products_sorted_in_the_right_way(page):
    page.goto(FRONTEND_URL)

    page.get_by_test_id("sort-select").select_option("По цене")
    page.get_by_test_id("order-select").select_option("По возрастанию")
    page.get_by_test_id("apply-filters").click()

    price_locator = page.get_by_test_id("product-price")
    raw_prices = price_locator.all_inner_texts()

    prices = [parse_price(raw_price) for raw_price in raw_prices]
    assert prices == sorted(prices), (
        f"Цены должны быть отсортированы по возрастанию. "
        f"Получили: {prices}"
    )

def test_second_page_available(page):
    page.goto(FRONTEND_URL)
    page.get_by_test_id("pagination-next")
    expect(page.get_by_role("link", name="2", exact=True))