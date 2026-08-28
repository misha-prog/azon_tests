import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.ui


def test_catalog_title_is_wrong_on_purpose(page):
    catalog_page = CatalogPage(page).open()

    expect(catalog_page.title).to_have_text("Витрина")