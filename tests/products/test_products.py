import uuid
from decimal import Decimal

class TestProducts:

    def test_get_products_return_paginated_catalog(self, api_manager):
        response = api_manager.products_api.get_products()

        data = response.json()
        assert data["total"] > 0
        assert len(data["items"]) <= data["size"]

    def test_products_price_filter(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"price_min": 5000, "size": 100}
        )

        products = response.json()["items"]
        assert products, "Ожидали хотя бы один товар дороже 5000"
        for product in products:
            assert Decimal(product["price"]) >= 5000

    def test_first_product_is_valid(self, api_manager):
        response = api_manager.products_api.get_product("0169e2e8-f8bf-5a3a-9a38-26ec84db79ee")

        assert response.json()["id"] == "0169e2e8-f8bf-5a3a-9a38-26ec84db79ee"

    def test_first_product_is_valid_negative(self, api_manager):
        response = api_manager.products_api.get_product(f"{str(uuid.uuid4())}", expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_create_review(self, authenticated_user, api_manager):
        products = api_manager.products_api.get_products()
        product_id = products.json()["items"][0]["id"]
        response = api_manager.products_api.create_review(product_id, 5, "aboba", 201)

        assert response.json()["rating"] == 5
        assert response.json()["text"] == "aboba"