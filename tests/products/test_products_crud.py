import pytest
from data.products import ProductData
from utils.marks import requires_admin

pytestmark = [pytest.mark.products, pytest.mark.regression]

@requires_admin
class TestProductsCrud:

    def test_create_product(self, authenticated_admin, category_id):
        ...


    @pytest.mark.slow
    def test_catalog_keeps_all_created_products(self, api_manager, category_id):
        created = []
        for _ in range(10):
            product_data = ProductData.create_full_product(category_id)
            created.append(api_manager.products_api.create_product(product_data).json())

        response = api_manager.products_api.get_products(
            params={"category_id": category_id, "size": 100, "sort_by": "created_at"}
        )
        catalog_ids = {item["id"] for item in response.json()["items"]}

        try:
            assert {product["id"] for product in created} <= catalog_ids
        finally:
            for product in created:
                api_manager.products_api.delete_product(product["id"])

@pytest.mark.negative
class TestProductsNegative:

    @pytest.mark.roles
    def test_create_without_token(self, authenticated_admin, category_id):
        ...