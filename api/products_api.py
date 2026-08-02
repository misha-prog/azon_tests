from unittest import expectedFailure

from config.hosts import PRODUCT_URL
from requester.custom_requester import CustomRequester


class ProductsAPI(CustomRequester):
    PRODUCTS_ENDPOINT = "/api/v1/products"

    def __init__(self, session):
        super().__init__(session, base_url=PRODUCT_URL)

    def get_products(self, params=None, expected_status=200):
        return self.send_request("GET", self.PRODUCTS_ENDPOINT, params=params, expected_status=expected_status)

    def get_product(self, product_id, expected_status=200):
        return self.send_request("GET", f"{self.PRODUCTS_ENDPOINT}/{product_id}", expected_status=expected_status)

    def create_review(self, product_id, rating: int, text: str, expected_status=200):
        return self.send_request("POST", f"{self.PRODUCTS_ENDPOINT}/{product_id}/reviews", json={"rating": rating, "text": text},expected_status=expected_status)
