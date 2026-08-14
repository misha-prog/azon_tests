import pytest
from decimal import Decimal
from uuid import UUID

from tests.conftest import db_guard
from utils.marks import requires_db, requires_admin

from data.products import ProductData

pytestmark = [pytest.mark.db, pytest.mark.products, requires_db, requires_admin]


class TestProductsInDB:

    @pytest.mark.usefixtures("db_guard")
    def test_created_product_is_saved_in_db(self, created_product, db):
        row = db.product.get_product(created_product.id)

        assert row is not None, "товар создан через API, но строки в базе нет"
        assert row["sku"] == created_product.sku
        assert row["price"] == created_product.price
        assert row["stock"] == created_product.stock
        assert row["deleted_at"] is None
        assert row["is_seed"] is False

    @pytest.mark.usefixtures("db_guard")
    def test_product_author_lives_in_another_database(self, created_product, db):
        # created_by приходит из JWT: id пользователя, которого хранит другой сервис
        product = db.product.get_product(created_product.id)

        author = db.auth.get_user(product["created_by"])

        assert author is not None, "автор товара должен существовать в azon_auth"
        assert author["role"] in ("MANAGER", "ADMIN")

    @pytest.mark.usefixtures("db_guard")
    def test_deleted_product_stays_in_db(self, api_manager, admin_manager, authenticated_user,created_product, db):
        admin_manager.products_api.delete_product(created_product.id)

        # покупателю товара больше нет...
        api_manager.products_api.get_product(created_product.id, expected_status=404)

        # ...а в базе строка на месте: удаление мягкое
        row = db.product.get_product(created_product.id)

        assert row is not None, "soft delete: строка должна остаться в базе"
        assert row["deleted_at"] is not None, "у удалённого товара проставляется deleted_at"

    @pytest.mark.usefixtures("db_guard")
    def test_deleted_products_swap_status(self, admin_manager, db, category_id):
        base_cnt_products = db.product.count_active_products(category_id)
        product = admin_manager.products_api.create_product(ProductData.create_full_product(category_id))

        updated_db = db.product.count_active_products(category_id)

        assert (base_cnt_products+1) == updated_db, "количество товаров после добавления осталось равным в бд"

        admin_manager.products_api.delete_product(product.json()["id"])
        cnt_after_del = db.product.count_active_products(category_id)

        assert base_cnt_products == cnt_after_del, "количество товаров после удаления лишнего не совпало"

    @pytest.mark.usefixtures("db_guard")
    def test_price_of_product_at_moment_of_add(self, admin_manager, category_id, db, authenticated_user, api_manager, created_product):
        api_manager.cart_api.add_item(ProductData.cart_item_data(created_product.id, quantity=2))
        new_price = ProductData.change_price()

        admin_manager.products_api.update_price(created_product.id, new_price)

        items = db.product.get_cart_items(authenticated_user["id"])
        assert len(items) == 1
        assert items[0]["quantity"] == 2
        assert items[0]["price_at_add"] == float(created_product.price), "в корзине - цена на момент добавления"

        cart = api_manager.cart_api.get_cart().json()
        assert float(cart["items"][0]["current_price"]) == float(str(new_price["price"]))
        assert cart["items"][0]["price_changed"] is True


    @pytest.mark.usefixtures("db_guard")
    def test_is_api_and_db_equal(self, db, authenticated_admin, api_manager, category_id):
        products_in_api = api_manager.products_api.get_products(params={"size": 100})
        total_in_api = len(products_in_api.json()["items"])

        total_in_db = db.product.count_all_products()

        # Проверяем то что количество товаров совпало и в апи и в бд
        assert total_in_api == total_in_db, "Количество товар в API и БД не совпало"

        # Добавляем продукт в апи и проверяем что цифры стока выросли и в апи и в бд
        product = api_manager.products_api.create_product(ProductData.create_full_product(category_id))

        products_in_api_after = api_manager.products_api.get_products(params={"size": 100})
        total_in_api_after = len(products_in_api_after.json()["items"])

        total_in_db_after = db.product.count_all_products()

        # Проверка на то что товаров одинаковое кол-во и там и тут после добавления
        assert total_in_api_after == total_in_db_after, (
            "Количество товаров было увеличено, "
            "но в разных базах кол-во товаров различается"
        )
        api_manager.products_api.delete_product(product.json()["id"])


    @pytest.mark.usefixtures("db_guard")
    def test_bin_plus_db(self, admin_manager, authenticated_user, db, category_id, api_manager, created_product):
        product_id = str(created_product.id)
        api_manager.cart_api.add_item({"product_id": product_id, "quantity": 3})

        items_in_cart = db.product.get_cart_items(authenticated_user["id"])
        assert str(items_in_cart[0]["product_id"]) == product_id
        assert items_in_cart[0]["quantity"] == 3
        assert items_in_cart[0]["price_at_add"] == Decimal(created_product.price)


    @pytest.mark.usefixtures("db_guard")
    def test_order_plus_join(self, created_product, db, api_manager, authenticated_user):
        api_manager.cart_api.add_item({"product_id": str(created_product.id), "quantity": 1})

        order = api_manager.payment_api.checkout()
        order_id = order.json()["id"]
        db_response = db.payment.get_order_by_id(order_id)

        assert db_response[0]["product_id"] == created_product.id
        assert db_response[0]["quantity"] == 1
        assert db_response[0]["order_id"] == UUID(order_id)
        assert db_response[0]["unit_price"] == Decimal(created_product.price)
