import uuid
from unittest.mock import MagicMock

from api.reviews_api import ReviewsAPI
from config.hosts import PRODUCT_URL

REVIEW_ID = uuid.uuid4()
def test_delete_review_without_network():
    response = MagicMock()
    response.status_code = 204
    response.text = ""
    response.elapsed.total_seconds.return_value = 0.01
    response.request_method = "DELETE"
    response.request_url = f"{PRODUCT_URL}/api/v1/reviews/{REVIEW_ID}"
    response.request.body = None

    session = MagicMock()
    session.request.return_value = response
    session.headers = {}

    ReviewsAPI(session).delete_review(REVIEW_ID)

    session.request.assert_called_once_with(
        "DELETE", f"{PRODUCT_URL}/api/v1/reviews/{REVIEW_ID}", timeout=10
    )