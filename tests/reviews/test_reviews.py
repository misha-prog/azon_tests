import pytest

from data.review import ReviewData
from models.reviews import ReviewResponse, ReviewsPage
from utils.marks import requires_admin

pytestmark = [pytest.mark.reviews, pytest.mark.regression, requires_admin]


class TestReviews:
    @pytest.mark.smoke
    @pytest.mark.contract
    def test_user_can_leave_review(self, api_manager, authenticated_user, created_product):
        review_request = ReviewData.create_full_review()

        response = api_manager.reviews_api.leave_review(
            created_product.id, review_request
        )
        review = ReviewResponse.model_validate(response.json())

        assert str(review.user_id) == authenticated_user["id"]
        assert review.product_id == created_product.id
        assert review.rating == review_request.rating
        assert review.text == review_request.text

    @pytest.mark.negative
    def test_second_review_rejected_from_same_user(
        self, authenticated_user, api_manager, created_product
    ):
        first_review = ReviewResponse.model_validate(
            api_manager.reviews_api.leave_review(
                created_product.id, ReviewData.create_full_review()
            ).json()
        )

        response = api_manager.reviews_api.leave_review(
            created_product.id,
            ReviewData.create_full_review(),
            expected_status=409,
        )
        page = ReviewsPage.model_validate(
            api_manager.reviews_api.check_reviews(created_product.id).json()
        )

        assert response.json()["error"]["code"] == "REVIEW_EXISTS"
        assert str(first_review.user_id) == authenticated_user["id"]
        assert page.total == 1
        assert page.items[0].id == first_review.id

    @pytest.mark.negative
    @pytest.mark.roles
    def test_foreign_review_cannot_be_edited(self, other_user, created_review):
        update = ReviewData.update_review_text()

        response = other_user.reviews_api.change_review(
            created_review.id, update, expected_status=403
        )
        page = ReviewsPage.model_validate(
            other_user.reviews_api.check_reviews(created_review.product_id).json()
        )
        actual_review = next(
            review for review in page.items if review.id == created_review.id
        )

        assert response.json()["error"]["code"] == "NOT_REVIEW_OWNER"
        assert actual_review.user_id == created_review.user_id
        assert actual_review.text == created_review.text
