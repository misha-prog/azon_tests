import requests
import pytest


from api.api_manager import ApiManager
from data.products import ProductData
from data.users import UserData
from utils.data_generator import DataGenerator
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE


@pytest.fixture(scope="session")
def api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()

@pytest.fixture(autouse=True)
def clean_auth_header(api_manager):
    yield
    api_manager.auth_api.session.headers.pop("Authorization", None)

@pytest.fixture
def registered_user(api_manager):
    user_data = UserData.registration_data()
    response = api_manager.auth_api.register_user(user_data)
    return {**user_data, "id": response.json()["id"]}


@pytest.fixture(scope="function")
def authenticated_user(api_manager):
    user_data = UserData.registration_data()
    register_response = api_manager.auth_api.register_user(user_data)
    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))
    return {**user_data, "id": register_response.json()["id"]}

@pytest.fixture(scope="function")
def created_product(api_manager, authenticated_admin, category_id):
    product = ProductData.create_full_product()
    product["category_id"] = category_id
    add_product = api_manager.products_api.create_product(product)
    created = add_product.json()
    product_id = created["id"]
    yield created
    api_manager.products_api.delete_product(product_id)

@pytest.fixture(scope="function")
def authenticated_manager(api_manager):
    user_data = UserData.registration_data_manager()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль менеджера задалась
    assert register_response.json()["role"] == "MANAGER", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env")

    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))
    return {**user_data, "id": register_response.json()["id"]}

@pytest.fixture(scope="function")
def authenticated_admin(api_manager):
    user_data = UserData.registration_data_admin()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль менеджера задалась
    assert register_response.json()["role"] == "ADMIN", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env")

    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))
    return {**user_data, "id": register_response.json()["id"]}

@pytest.fixture(scope="function")
def new_body_product(api_manager):
    name = DataGenerator.generate_name_of_product()
    description = DataGenerator.generate_description()
    stock = DataGenerator.generate_stock()
    all_categories = api_manager.products_api.get_categories()
    category_id = all_categories.json()[0]["id"]
    return {"name": name, "description": description, "stock": stock, "category_id": category_id}

@pytest.fixture(scope="function")
def category_id(api_manager):
    response = api_manager.products_api.get_categories(params={"size": 1})
    data = response.json()

    if isinstance(data, dict) and "items" in data:
        categories = data["items"]
    else:
        categories = data

    assert categories, "Не удалось получить категории"

    return categories[0]["id"]


@pytest.mark.smoke
def test_health(api_manager):
    ...
@pytest.mark.skip(reason="AZON-101: экспорт каталока в CSV еще не реализован")
def test_export_catalog_to_csv():
    assert False