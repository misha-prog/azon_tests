import uuid
from decimal import Decimal

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
        product_create = api_manager.products_api.get_product(created_product["id"])
        assert created_product == product_create.json(), (
            f"Данные не совпали с ответом и выдало : {product_create.text}"
        )

    def test_created_product_can_be_deleted(self, api_manager, authenticated_admin):
        # Проверка на то что можем удалить товар, который создали
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

    def test_get_product_by_invalid_id(self, api_manager):
        response = api_manager.products_api.get_product(f"{str(uuid.uuid4())}", expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND", (
            f"Хотели получить ошибку о том что не нашли товар "
            f"с выдуманным айди, но север выдал ошибку такую : {response.text}"
        )

    def test_access_to_create_product_without_access(self, api_manager, authenticated_user):
        # Создаем шаблон продукта для дальнейшей его выгрузки на сервер
        product = ProductData.create_full_product()
        products_list = api_manager.products_api.get_products()

        # Присваиваем нашему продукту существующий айди категории
        category_id = products_list.json()["items"][0]["category_id"]
        product["category_id"] = category_id

        response = api_manager.products_api.create_product(product, 403)

        assert response.json()["error"]["code"] == "FORBIDDEN", (
            f"После создания товара без доступа ожидали получить ошибку "
            f"'FORBIDDEN', а получили {response.text}"
        )

    def test_delete_seed_product(self, api_manager, authenticated_admin):
        # Смотрим на все товары и выбираем первый для удаления
        products_list = api_manager.products_api.get_products(params={"is_seed": True})
        product = products_list.json()["items"][0]

        # Пытаемся удалить seed-товар в роли админа
        response = api_manager.products_api.delete_product(product["id"], 403)

        assert response.json()["error"]["code"] == "SEED_PROTECTED", (
            f"Удаляли товар который защищен от удаления, "
            f"ожидали увидеть ошибку 'SEED_PROTECTED', но пришло: {response.text}"
        )

    def test_get_invalid_category(self, api_manager, authenticated_admin):
        response = api_manager.products_api.get_products(params={"category_id": str(uuid.uuid4())}, expected_status=200)

        assert response.json()["items"] == [], (
            f"Пытались получить товар с несуществующей категорией, "
            f"ожидали увидеть непустой список, а получили {response.text}"
        )

    def test_invalid_body_of_product(self, api_manager, authenticated_admin):
        # Тут создали обычный товар
        product = ProductData.create_full_product()
        products_list = api_manager.products_api.get_products()
        category_id = products_list.json()["items"][0]["category_id"]
        product["category_id"] = category_id

        # А тут уже задаем неправильный параметр в тело
        product["stock"] = -1

        response = api_manager.products_api.create_product(product, 422)

        assert "detail" in response.json(), (
            f"Ожидали увидеть стандартный ответ FastAPI, "
            f"но получили : {response.text}"
        )