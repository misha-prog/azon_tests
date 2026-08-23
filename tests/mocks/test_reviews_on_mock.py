"""1. стаб на список отзывов - ответ разбирается моделью ReviewsPage;

2. стаб на 500 с телом ошибки - падение читаемое, код INTERNAL_ERROR виден в сообщении;

3. журнал запросов: при обновлении отзыва только с текстом в теле уезжает одно поле - это проверка exclude_none из Темы 2.

"""
import json
import uuid

import pytest
import requests

from api.reviews_api import ReviewsAPI
from config.mock import MOCK_URL
from data.review import ReviewData
from models.reviews import ReviewsPage
from tests.mocks.stubs import ProductStubs, review


JSON_HEADERS = {"Content-Type": "application/json"}

pytestmark = [pytest.mark.mock]


def test_reviews_stub(wiremock):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.get_reviews_list(product_id))

    with requests.Session() as session:
        response = ReviewsAPI(session, base_url=MOCK_URL).check_reviews(product_id)

    page = ReviewsPage.model_validate(response.json())

    assert page.total == 1
    assert page.page == 1
    assert page.size == 20
    assert page.pages == 1
    assert len(page.items) == 1
    assert str(page.items[0].product_id) == product_id
    assert 1 <= page.items[0].rating <= 5


def test_code_500_readable(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.server_error(product_id))

    with pytest.raises(AssertionError) as error:
        mock_products_api.get_product(product_id)

    assert "ожидали статус 200, получили 500" in str(error.value)
    assert "INTERNAL_ERROR" in str(error.value)


def test_update_sends_only_filled_fields(wiremock):
    wiremock.add_stub(
        {
            "request": {"method": "PATCH", "urlPathPattern": "/api/v1/reviews/.+"},
            "response": {"status": 200, "headers": JSON_HEADERS, "jsonBody": review()},
        }
    )
    review_id = uuid.uuid4()
    update = ReviewData.update_review_text()

    with requests.Session() as session:
        ReviewsAPI(session, base_url=MOCK_URL).change_review(review_id, update)

    sent = wiremock.find_requests(
        {"method": "PATCH", "urlPath": f"/api/v1/reviews/{review_id}"}
    )[0]
    assert json.loads(sent["body"]) == {"text": update.text}
