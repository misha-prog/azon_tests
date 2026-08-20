import pytest
from data.review import ReviewData
from models.reviews import ReviewResponse

pytestmark = [pytest.mark.db, pytest.mark.reviews]

@pytest.mark.usefixtures("db_guard", "authenticated_user")
def test_same_rating_and_text_in_db(created_product, created_review, db):
    response_db = db.product.get_review_from_product(created_review.id)

    assert response_db["text"] == created_review.text
    assert response_db["rating"] == created_review.rating


@pytest.mark.usefixtures("db_guard", "authenticated_user")
def test_second_review_doesnt_exist(created_product, created_review, db, api_manager):
    response_review = api_manager.reviews_api.leave_review(created_product.id, body=ReviewData.create_full_review(), expected_status=409)

    assert response_review.json()["error"]["code"] == "REVIEW_EXISTS"
    assert db.product.count_reviews(created_product.id) == 1

@pytest.mark.usefixtures("db_guard", "authenticated_user")
def test_moderation_deletes_row_and_leaves_a_trace(manager_manager, db, created_product, api_manager):
    """Отзыв удаляется по-настоящему - в отличие от товара, у которого удаление мягкое."""
    create_review = api_manager.reviews_api.leave_review(created_product.id, ReviewData.create_full_review())
    created_review = ReviewResponse.model_validate(create_review.json())
    manager_manager.reviews_api.delete_review(created_review.id)


    assert db.product.get_review_from_product(created_review.id) is None, "строка отзыва должна была исчезнуть"

    record = db.product.get_moderation_record(created_review.id)
    assert record is not None, "модерация чужого отзыва обязана попасть в audit_log"
    assert record["payload"]["author"] == str(created_review.user_id)


