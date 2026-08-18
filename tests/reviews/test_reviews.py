import pytest

from api import reviews_api
from utils.marks import requires_admin

pytestmark = [pytest.mark.reviews, pytest.mark.regression, requires_admin]


class TestReviews:

    @pytest.mark.smoke
    @pytest.mark.contract
    def test_user_can_leave_review(self, api_manager, authenticated_user, created_product):
        response = api_manager.reviews_api.leave_review(created_product.id,body={"rating": 1, "text": "abvbvb", "summary": 10}, expected_status=422)
        assert response.json()["detail"][0]["type"] == "extra_forbidden"


    @pytest.mark.negative
    def test_second_review_rejected_from_same_user(self, authenticated_user, api_manager, created_product):
        ...

    @pytest.mark.negative
    @pytest.mark.roles
    def test_foreign_review_cannot_be_edited(self, other_user, created_review):
        ...