from config.hosts import PRODUCT_URL
from requester.custom_requester import CustomRequester

PRODUCTS_ENDPOINT = "/api/v1/products"
REVIEWS_ENDPOINT = "/api/v1/reviews"


class ReviewsAPI(CustomRequester):

    def __init__(self, session, base_url=PRODUCT_URL):
        super().__init__(session, base_url)

    def check_reviews(self, product_id, params=None, expected_status=200, **kwargs):
        return self.send_request("GET", f"{PRODUCTS_ENDPOINT}/{product_id}/reviews", params=params, expected_status=expected_status, **kwargs)

    def leave_review(self, product_id, body, expected_status=201, **kwargs):
        return self.send_request("POST", f"{PRODUCTS_ENDPOINT}/{product_id}/reviews", json=body, expected_status=expected_status, **kwargs)

    def change_review(self, review_id, body, expected_status=200, **kwargs):
        return self.send_request("PATCH", f"{REVIEWS_ENDPOINT}/{review_id}", json=body, expected_status=expected_status, **kwargs)

    def delete_review(self, review_id, expected_status=204, **kwargs):
        return self.send_request("DELETE", f"{REVIEWS_ENDPOINT}/{review_id}", expected_status=expected_status, **kwargs)
