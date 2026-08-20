"""1. стаб на список отзывов - ответ разбирается моделью ReviewsPage;

2. стаб на 500 с телом ошибки - падение читаемое, код INTERNAL_ERROR виден в сообщении;

3. журнал запросов: при обновлении отзыва только с текстом в теле уезжает одно поле - это проверка exclude_none из Темы 2.

"""
import uuid
import requests
import pytest
import json

from api.reviews_api import ReviewsAPI
from config.mock import MOCK_URL
from data.review import ReviewData
from tests.mocks.stubs import ProductStubs
from stubs import review


JSON_HEADERS = {"Content-Type": "application/json"}

pytestmark = [pytest.mark.mock]


def test_reviews_stub(wiremock):
    session = requests.Session()
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.get_reviews_list(product_id))

    ReviewsAPI(session, base_url="http://localhost:8090").check_reviews(product_id)

    response = wiremock.find_requests({
        "method": "GET",
        "urlPath": f"/api/v1/products/{product_id}/reviews"
    })[0]

    assert response["body"] is not None, (
        f"Тело запроса пусто либо содержит не то,"
        f"{response['body']}"
    )

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

    sent = wiremock.find_requests({"method": "PATCH", "urlPath": f"/api/v1/reviews/{review_id}"})[0]
    assert json.loads(sent["body"]) == {"text": update.text}