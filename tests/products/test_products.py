import uuid

import pytest
from decimal import Decimal
from pydantic import ValidationError
from uuid import UUID

from data.products import ProductData
from models.products import ProductResponse, ProductsPage, ProductRequest
from utils.marks import requires_admin


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

    @pytest.mark.usefixtures("authenticated_user")
    def test_first_product_is_valid(self, api_manager):
        products_list = api_manager.products_api.get_products()
        product_id = products_list.json()["items"][0]["id"]
        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    def test_get_product(self, api_manager, created_product):
        # Тест на получение только что созданного товара
        product_id = created_product.id
        response_id = api_manager.products_api.get_product(product_id)

        product = ProductResponse.model_validate(response_id.json())

        assert UUID(response_id.json()["id"]) == product_id, (
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
                f"а товар этот : {item}"
            )

    def test_max_price_product(self, api_manager, authenticated_user):
        # Получаем список отсортированных товаров
        products_list = api_manager.products_api.get_products(params={"sort_by": "price", "order": "desc","size": 50})

        # Проверяем что первый товар и правда дороже всех остальных
        max_price = float(products_list.json()["items"][0]["price"])
        for item in products_list.json()["items"]:
            assert float(item["price"]) <= max_price, (
                f"Товары отсортированы неверно, "
                f"у первого товара должна была быть самая высокая цена, "
                f"но нашли товар с большей ценой : {item['price']}"
            )

    def test_created_product_accessible(self, api_manager, created_product):
        # Проверка на то что товар создается и данные совпадают с ответом
        product_create = api_manager.products_api.get_product(created_product.id)

        fetched_product = ProductResponse.model_validate(product_create.json())

        assert created_product == fetched_product, (
            f"Данные не совпали с ответом и выдало : {product_create.text}"
        )

    def test_created_product_can_be_deleted(self, api_manager, authenticated_admin, category_id):
        # Проверка на то что можем удалить товар, который создали
        product = ProductData.create_full_product(category_id)
        product.category_id = category_id

        response = api_manager.products_api.create_product(product)
        product_id = response.json()["id"]
        # Создали объект без фикстуры, потому что фикстура сама чистит за собой данные

        api_manager.products_api.delete_product(product_id=product_id)
        # Удаляем только что созданный объект

        is_accessible = api_manager.products_api.get_product(product_id)
        assert is_accessible.json()["is_available"] == False, (
            f"Проверяли, что товар недоступен, но получили "
            f"{is_accessible.text}"
        )

    def test_update_price(self, api_manager, authenticated_admin, category_id):
        product = ProductData.create_full_product(category_id)
        product.category_id = category_id

        response = api_manager.products_api.create_product(product)
        product_id = response.json()["id"]
        api_manager.products_api.update_price(product_id, new_price={"price": 99999}, expected_status=200)

        updated_product_price = api_manager.products_api.get_product(product_id)
        api_manager.products_api.delete_product(product_id)
        assert float(updated_product_price.json()["price"]) == 99999.00, (
            f"Проверяли что новая цена применилась к товару, "
            f"но этого не произошло и получили цену : {updated_product_price.json()["price"]}"
        )

    def test_update_product(self, api_manager, authenticated_admin, created_product, new_body_product):
        product_id = created_product.id
        response = api_manager.products_api.update_product(product_id, new_body_product)

        assert response.json()["name"] == new_body_product["name"], (
            f"Обновили продукт новыми данными но не получилось, "
            f"и выдало ошибку {response.text}"
        )

    @pytest.mark.usefixtures("authenticated_admin")
    def test_create_product(self, category_id, api_manager):
        product_request = ProductData.create_full_product(category_id)

        response = api_manager.products_api.create_product(product_request)

        product = ProductResponse.model_validate(response.json())
        assert product.name == product_request.name
        assert product.sku == product_request.sku
        assert product.price == product_request.price
        assert product.stock == product_request.stock
        assert product.is_available is True

    def test_get_created_product(self, api_manager, created_product):
        response = api_manager.products_api.get_product(created_product.id)

        assert ProductResponse.model_validate(response.json()) == created_product

    def test_products_price_filter_1(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"price_min": 5000, "size": 100}
        )

        page = ProductsPage.model_validate(response.json())
        assert page.items, "Ожидали хотя бы один товар дороже 5000"
        # price уже Decimal - руками ничего не приводим
        assert all(product.price >= 5000 for product in page.items)

    def test_model_reject_zero_price(self):
        product_request = ProductData.create_full_product(uuid.uuid4())

        with pytest.raises(ValidationError) as error:
            ProductRequest.model_validate({**product_request.model_dump(), "price": 0})

        assert error.value.errors()[0]["type"] == "greater_than"

    @staticmethod
    def product_with_invalid_price(category_id) -> dict:
        product = ProductData.create_full_product(category_id)
        return {**product.model_dump(mode="json"), "price": 0}

class TestProductsNegative:

    def test_get_product_by_invalid_id(self, api_manager):
        response = api_manager.products_api.get_product(f"{str(uuid.uuid4())}", expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND", (
            f"Хотели получить ошибку о том что не нашли товар "
            f"с выдуманным айди, но север выдал ошибку такую : {response.text}"
        )

    def test_access_to_create_product_without_access(self, api_manager, authenticated_user, category_id):
        # Создаем шаблон продукта для дальнейшей его выгрузки на сервер
        product = ProductData.create_full_product(category_id)
        products_list = api_manager.products_api.get_products()

        # Присваиваем нашему продукту существующий айди категории
        product.category_id = category_id

        response = api_manager.products_api.create_product(product, 403)

        assert response.json()["error"]["code"] == "FORBIDDEN", (
            f"После создания товара без доступа ожидали получить ошибку "
            f"'FORBIDDEN', а получили {response.text}"
        )

    @requires_admin
    def test_delete_seed_product(self, api_manager, authenticated_admin):
        # Смотрим на все товары и выбираем первый для удаления
        products_list = api_manager.products_api.get_products()
        product = dict()
        for item in products_list.json()["items"]:
            if item["is_seed"] == True:
                product = item
                break

        # Пытаемся удалить seed-товар в роли админа
        response = api_manager.products_api.delete_product(product["id"], 403)

        assert response.json()["error"]["code"] == "SEED_PROTECTED", (
            f"Удаляли товар который защищен от удаления, "
            f"ожидали увидеть ошибку 'SEED_PROTECTED', но пришло: {response.text}"
        )

    @requires_admin
    def test_get_invalid_category(self, api_manager, authenticated_admin):
        response = api_manager.products_api.get_products(params={"category_id": str(uuid.uuid4())}, expected_status=200)

        assert response.json()["items"] == [], (
            f"Пытались получить товар с несуществующей категорией, "
            f"ожидали увидеть непустой список, а получили {response.text}"
        )

    @requires_admin
    def test_invalid_body_of_product(self, api_manager, authenticated_admin, category_id):
        # Тут создали обычный товар
        product = ProductData.create_full_product(category_id)
        product.category_id = category_id

        # А тут уже задаем неправильный параметр в тело
        product.stock = -1

        response = api_manager.products_api.create_product(product, 422)

        assert "detail" in response.json(), (
            f"Ожидали увидеть стандартный ответ FastAPI, "
            f"но получили : {response.text}"
        )

    def test_create_product_without_token(self, api_manager, category_id):
        product = ProductData.create_full_product(category_id)
        product.category_id = category_id

        response = api_manager.products_api.create_product(product, 401)
        assert response.json(), (
            f"Пытались создать товар без токена вообще и ожидали код ошибки 401,  "
            f"но получили ошибку : {response.text}"
        )

    @requires_admin
    def test_create_product_with_invalid_category(self, api_manager, authenticated_admin):
        invalid_category_id = uuid.uuid4()
        product = ProductData.create_full_product(invalid_category_id)


        response = api_manager.products_api.create_product(product, 404)

        assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND", (
            f"Создали товар с неверной категорией и ожидали ошибку, "
            f"что категория не найдена, но получили : {response.text}"
        )

    def test_change_price_by_manager(self, api_manager, authenticated_manager):
        products = api_manager.products_api.get_products()
        product_id = products.json()["items"][0]["id"]

        response = api_manager.products_api.update_price(product_id, "10000", 403)

        assert "error" in response.json(), (
            f"Ждали ошибку о том что менеджер не может обновить цену,"
            f"но получили следующее сообщение : {response.text}"
        )

    @requires_admin
    def test_stock_update_with_famous_bug(self, created_product, admin_manager, api_manager, authenticated_user):
        admin_manager.products_api.update_product(created_product.id, {"stock": 0})

        response = api_manager.products_api.get_products({"in_stock": True, "size": 100})

        for item in response.json()["items"]:
            assert str(created_product.id) != item["id"], (
                "Созданный товар как то оказался"
                "в выдаче, хотя мы задали ему сток 0"
            )


@pytest.mark.xfail(reason="AZON-142: фильтр in_stock=false не отбирает товары без остатка", strict=True)
def test_filter_out_of_stock(api_manager):
    response = api_manager.products_api.get_products(
        params={"in-stock": False, "size": 100}
    )

    items = response.json()["items"]
    assert all(item["stock"] == 0 for item in items)

@pytest.mark.parametrize(
    "field, value, expected_type",
    [
        ("sku", "AZ 001 с пробелами", "string_pattern_mismatch"),
        ("name", "", "string_too_short"),
        ("stock", -1, "greater_than_equal"),
        ("price", "1000001", "less_than_equal"),
    ],
)

@pytest.mark.usefixtures("authenticated_admin")
def test_model_rejects_bad_field(field, value, expected_type, category_id, api_manager):
    data = ProductData.create_full_product(category_id).model_dump()

    data[field] = value

    with pytest.raises(ValidationError) as exc_info:
        ProductRequest(**data)

    errors = exc_info.value.errors()
    assert any(error["type"] == expected_type for error in errors)