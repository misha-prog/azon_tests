import requests
import pytest


from api.api_manager import ApiManager
from api.payment_api import PaymentAPI
from data.products import ProductData
from data.review import ReviewData
from data.users import UserData
from db.db_manager import DBManager
from models.orders import OrderResponse
from models.reviews import ReviewResponse
from utils.data_generator import DataGenerator
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from models.users import RegisteredUser, UserResponse
from models.products import ProductResponse
from uuid import UUID
from api.products_api import ProductsAPI
from config.mock import MOCK_URL
from mocks.wiremock_admin import WireMockAdmin


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
def registered_user(api_manager) -> RegisteredUser:
    registration = UserData.registration_data()

    response = api_manager.auth_api.register_user(registration)

    return RegisteredUser(
        registration=registration, profile=UserResponse.model_validate(response.json())
    )


@pytest.fixture
def created_product(admin_manager, category_id) -> ProductResponse:
    product_request = ProductData.create_full_product(category_id)

    response = admin_manager.products_api.create_product(product_request)
    product = ProductResponse.model_validate(response.json())

    yield product

    try:
        admin_manager.products_api.delete_product(product.id)
    except AssertionError:
        pass

@pytest.fixture(scope="function")
def authenticated_user(api_manager):
    user_data = UserData.registration_data()
    register_response = api_manager.auth_api.register_user(user_data)
    api_manager.auth_api.authenticate((user_data.email, user_data.password))
    return {**user_data.model_dump(), "id": register_response.json()["id"]}

'''
@pytest.fixture(scope="function")
def created_product(api_manager, authenticated_admin, category_id):
    product = ProductData.create_full_product()
    product["category_id"] = category_id
    add_product = api_manager.products_api.create_product(product)
    created = add_product.json()
    product_id = created["id"]
    yield created
    api_manager.products_api.delete_product(product_id)
'''

@pytest.fixture(scope="function")
def authenticated_manager(api_manager):
    user_data = UserData.registration_data_manager()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль менеджера задалась
    assert register_response.json()["role"] == "MANAGER", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env")

    api_manager.auth_api.authenticate((user_data.email, user_data.password))
    return {**user_data.model_dump(), "id": register_response.json()["id"]}

@pytest.fixture(scope="function")
def authenticated_admin(api_manager):
    user_data = UserData.registration_data_admin()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль админа задалась
    assert register_response.json()["role"] == "ADMIN", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env")

    api_manager.auth_api.authenticate((user_data.email, user_data.password))
    return {**user_data.model_dump(), "id": register_response.json()["id"]}

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
    category_uuid = response.json()[0]["id"]
    return UUID(category_uuid)

@pytest.mark.smoke
def test_health(api_manager):
    ...
@pytest.mark.skip(reason="AZON-101: экспорт каталока в CSV еще не реализован")
def test_export_catalog_to_csv():
    assert False

@pytest.fixture(autouse=True)
def warn_about_slow(request):
    if request.node.get_closest_marker("slow"):
        print(f"\n[!] {request.node.name} помечен slow - готовьтесь ждать")

def pytest_collection_modifyitems(items):
    """Нет кода админа в .env - пропускаем всё, что просит админскую фикстуру."""
    if ADMIN_INVITE_CODE:
        return
    skip_admin = pytest.mark.skip(reason="в .env нет ADMIN_INVITE_CODE")
    for item in items:
        if "authenticated_admin" in item.fixturenames:
            item.add_marker(skip_admin)

@pytest.fixture(scope="session")
def db():
    manager = DBManager()
    yield manager
    manager.close()

@pytest.fixture
def created_order(api_manager, authenticated_user, created_product):
    """Заказ из одного товара: кладём товар в корзину и оформляем заказ."""
    api_manager.cart_api.add_item(ProductData.cart_item_data(created_product.id))

    response = api_manager.payment_api.checkout()
    return response.json()

@pytest.fixture(scope="function")
def admin_manager():
    session = requests.Session()
    manager = ApiManager(session)

    admin_data = UserData.registration_data_admin()
    register_response = manager.auth_api.register_user(admin_data)

    assert register_response.json()["role"] == "ADMIN", (
        f"Инвайт-код не сработал, "
        f"роль {register_response.json()['role']}, проверь .env"
    )

    manager.auth_api.authenticate(
        (admin_data.email, admin_data.password)
    )

    yield manager

    session.close()

@pytest.fixture(scope="function")
def manager_manager():
    session = requests.Session()
    manager = ApiManager(session)

    manager_data = UserData.registration_data_manager()
    register_response = manager.auth_api.register_user(manager_data)

    assert register_response.json()["role"] == "MANAGER", (
        f"не сработал инвайт код,"
        f"роль {register_response.json()["role"]}, проверь .env"
    )

    manager.auth_api.authenticate(
        (manager_data.email, manager_data.password)
    )

    yield manager

    session.close()

@pytest.fixture(scope="function")
def db_guard(db):
    before_tests = db.product.count_all_products()
    yield before_tests
    after_tests = db.product.count_all_products()
    assert before_tests == after_tests, (
        "Количество строк в базе данных"
        "не совпало с тем, что было до тестов"
    )


@pytest.fixture
def wiremock():
    """Чистый WireMock перед каждым тестом: свои стабы, свой журнал запросов."""
    admin = WireMockAdmin()

    if not admin.is_running():
        pytest.skip(f"WireMock не отвечает на {MOCK_URL} - тесты с моками пропускаем")

    admin.reset()
    yield admin
    admin.session.close()


@pytest.fixture
def mock_products_api(wiremock):
    """Наш обычный ProductsAPI, только смотрит он не на стенд, а в мок."""
    session = requests.Session()
    yield ProductsAPI(session, base_url=MOCK_URL)
    session.close()

@pytest.fixture
def mock_payment_api():
    session = requests.Session()
    yield PaymentAPI(session, base_url=MOCK_URL)
    session.close()

@pytest.fixture
def created_review(api_manager, created_product, admin_manager):
    review = ReviewData.create_full_review()

    leaved_review = api_manager.reviews_api.leave_review(created_product.id, review)
    extracted_review = ReviewResponse.model_validate(leaved_review.json())
    yield extracted_review

@pytest.fixture
def other_user():
    session = requests.Session()
    other_manager = ApiManager(session)

    user_data = UserData.registration_data()
    register_response = other_manager.auth_api.register_user(user_data)
    other_manager.auth_api.authenticate((user_data.email, user_data.password))

    try:
        yield other_manager
    finally:
        session.close()

@pytest.fixture
def order(api_manager, authenticated_user, created_product):
    cart_item = {
        "product_id": str(created_product.id),
        "quantity": 1,
    }

    api_manager.cart_api.add_item(cart_item)
    response = api_manager.payment_api.checkout()
    created_order = OrderResponse.model_validate(response.json())

    assert created_order.status == "AWAITING_PAYMENT"

    return created_order