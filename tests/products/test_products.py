import uuid
from decimal import Decimal
from http.client import responses

from data.products import ProductData

class TestProductsPositive:

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

    def test_get_product(self, api_manager, created_product):
        # Тест на получение только что созданного товара
        response = api_manager.products_api.get_products()
        created_product["category_id"] = response.json()["items"][0]["category_id"]
        add_product = created_product
        product_id = add_product["id"]

        response_id = api_manager.products_api.get_product(product_id)

        assert response_id.json()["id"] == product_id, (
            f"Проверили что получили тот же товар что и отдали, "
            f"но что-то пошло не так и получили товар с айди: {product_id}"
        )

    def test_get_products_by_category(self, api_manager):
        # Тест на проверку категорий у товаров
        response = api_manager.products_api.get_products()

        first_item = response.json()["items"][0]

        response_category = api_manager.products_api.get_products(
            params={"category_id": first_item["category_id"]}
        )

        category_item = response_category.json()["items"]
        for item in category_item:
            # Проверяем что все товары из выбранной категории
            assert item["category_id"] == first_item["category_id"], (
                f"Попался товар не из той категории которой мы хотели, "
                f"а товар этот : {item[item]}"
            )

    def test_created_product_accessible(self, api_manager, created_product):
        # Проверка на то что товар создается и данные совпадают с ответом
        product_create = api_manager.products_api.get_product(created_product["id"])
        assert created_product == product_create.json()

    def test_created_product_can_be_deleted(self, api_manager, authenticated_admin):
        # Проверка на то что можем удалить товар который создали
        product = ProductData.create_full_product()
        products_list = api_manager.products_api.get_products()
        product_category_id = products_list.json()["items"][0]["category_id"]
        product["category_id"] = product_category_id

        response = api_manager.products_api.create_product(product)
        product_id = response.json()["id"]
        # Создали объект без фикстуры, потому что фикстура сама чистит за собой данные

        api_manager.products_api.delete_product(product_id=product_id)
        # Удаляем только что созданный объект

        assert api_manager.products_api.get_product(product_id)

    def test_update_price(self, api_manager, authenticated_admin):
        product = ProductData.create_full_product()
        products_list = api_manager.products_api.get_products()
        product_category_id = products_list.json()["items"][0]["category_id"]
        product["category_id"] = product_category_id

        response = api_manager.products_api.create_product(product)
        product_id = response.json()["id"]
        api_manager.products_api.update_price(product_id, new_price={"price": 99999}, expected_status=200)

        updated_product_price = api_manager.products_api.get_product(product_id)
        api_manager.products_api.delete_product(product_id)
        assert float(updated_product_price.json()["price"]) == 99999.00, (
            f"Проверяли что новая цена применилась к товару, "
            f"но этого не произошло и получили цену : {updated_product_price.json()["price"]}"
        )


class TestProductsNegative:

    def test_first_product_is_valid_negative(self, api_manager):
        response = api_manager.products_api.get_product(f"{str(uuid.uuid4())}", expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"
