from config.hosts import PRODUCT_URL
from requester.custom_requester import CustomRequester


class ProductsAPI(CustomRequester):
    PRODUCTS_ENDPOINT = "/api/v1/products"
    CATEGORIES_ENDPOINT = "/api/v1/categories"

    def __init__(self, session, base_url=PRODUCT_URL):
        super().__init__(session, base_url)

    def get_products(self, params=None, expected_status=200):
        return self.send_request(
            "GET",
            self.PRODUCTS_ENDPOINT,
            params=params,
            expected_status=expected_status,
        )

    def get_product(self, product_id, expected_status=200, timeout=10):
        return self.send_request(
            "GET",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}",
            expected_status=expected_status,
            timeout=timeout,
        )

    def get_categories(self, params=None, expected_status=200):
        return self.send_request(
            "GET",
            self.CATEGORIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    def create_review(self, product_id, rating: int, text: str, expected_status=200):
        return self.send_request(
            "POST",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}/reviews",
            json={"rating": rating, "text": text},
            expected_status=expected_status,
        )

    def create_product(self, product, expected_status=201):
        return self.send_request(
            "POST",
            self.PRODUCTS_ENDPOINT,
            json=product,
            expected_status=expected_status,
        )

    def delete_product(self, product_id, expected_status=204):
        return self.send_request(
            "DELETE",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}",
            expected_status=expected_status,
        )

    def update_price(self, product_id, new_price, expected_status=200):
        return self.send_request(
            "PATCH",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}/price",
            json=new_price,
            expected_status=expected_status,
        )

    def update_product(self, product_id, new_body, expected_status=200):
        return self.send_request(
            "PATCH",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}",
            json=new_body,
            expected_status=expected_status,
        )
