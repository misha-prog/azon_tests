from uuid import UUID

import allure
import pytest
import requests
from playwright.sync_api import expect
from requests import session

from api.api_manager import ApiManager
from api.payment_api import PaymentAPI
from api.products_api import ProductsAPI
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from config.db import DB_PASSWORD
from config.mock import MOCK_URL
from data.products import ProductData
from data.review import ReviewData
from data.users import UserData
from db.db_manager import DBManager
from models.orders import OrderResponse
from models.products import ProductResponse
from models.reviews import ReviewResponse
from models.users import RegisteredUser, UserResponse
from pages.login_page import LoginPage
from tests.mocks.wiremock_admin import WireMockAdmin
from utils.data_generator import DataGenerator


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


@pytest.fixture(scope="function")
def authenticated_manager(api_manager):
    if not MANAGER_INVITE_CODE:
        pytest.skip("в .env нет INVITE_CODE_MANAGER")

    user_data = UserData.registration_data_manager()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль менеджера задалась
    assert register_response.json()["role"] == "MANAGER", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env"
    )

    api_manager.auth_api.authenticate((user_data.email, user_data.password))
    return {**user_data.model_dump(), "id": register_response.json()["id"]}


@pytest.fixture(scope="function")
def authenticated_admin(api_manager):
    if not ADMIN_INVITE_CODE:
        pytest.skip("в .env нет INVITE_CODE_ADMIN")

    user_data = UserData.registration_data_admin()
    register_response = api_manager.auth_api.register_user(user_data)

    # Проверка на то что роль админа задалась
    assert register_response.json()["role"] == "ADMIN", (
        f"Инвайт-код не сработал, "
        f" роль {register_response.json()['role']}, проверь .env"
    )

    api_manager.auth_api.authenticate((user_data.email, user_data.password))
    return {**user_data.model_dump(), "id": register_response.json()["id"]}


@pytest.fixture(scope="function")
def new_body_product(api_manager):
    name = DataGenerator.generate_name_of_product()
    description = DataGenerator.generate_description()
    stock = DataGenerator.generate_stock()
    all_categories = api_manager.products_api.get_categories()
    category_id = all_categories.json()[0]["id"]
    return {
        "name": name,
        "description": description,
        "stock": stock,
        "category_id": category_id,
    }


@pytest.fixture(scope="function")
def category_id(api_manager):
    response = api_manager.products_api.get_categories(params={"size": 1})
    category_uuid = response.json()[0]["id"]
    return UUID(category_uuid)


@pytest.fixture(autouse=True)
def warn_about_slow(request):
    if request.node.get_closest_marker("slow"):
        print(f"\n[!] {request.node.name} помечен slow - готовьтесь ждать")


def pytest_collection_modifyitems(items):
    """Пропускает тесты до запуска фикстур, если нет нужных секретов."""
    admin_fixtures = {"authenticated_admin", "admin_manager", "created_product"}
    manager_fixtures = {"authenticated_manager", "manager_manager"}
    db_fixtures = {"db", "db_guard"}

    skip_admin = pytest.mark.skip(reason="в .env нет INVITE_CODE_ADMIN")
    skip_manager = pytest.mark.skip(reason="в .env нет INVITE_CODE_MANAGER")
    skip_db = pytest.mark.skip(reason="в .env нет DB_PASSWORD")

    for item in items:
        fixture_names = set(item.fixturenames)

        if not ADMIN_INVITE_CODE and fixture_names & admin_fixtures:
            item.add_marker(skip_admin)
        if not MANAGER_INVITE_CODE and fixture_names & manager_fixtures:
            item.add_marker(skip_manager)
        if not DB_PASSWORD and (
            item.get_closest_marker("db") or fixture_names & db_fixtures
        ):
            item.add_marker(skip_db)


@pytest.fixture(scope="session")
def db():
    if not DB_PASSWORD:
        pytest.skip("в .env нет DB_PASSWORD")

    manager = DBManager()
    yield manager
    manager.close()


@pytest.fixture
def created_order(api_manager, authenticated_user, created_product):
    """Заказ из одного товара: кладём товар в корзину и оформляем заказ."""
    api_manager.cart_api.add_item(
        ProductData.cart_item_data(created_product.id, quantity=1)
    )

    response = api_manager.payment_api.checkout()
    return response.json()


@pytest.fixture(scope="function")
def admin_manager():
    if not ADMIN_INVITE_CODE:
        pytest.skip("в .env нет INVITE_CODE_ADMIN")

    session = requests.Session()
    manager = ApiManager(session)

    admin_data = UserData.registration_data_admin()
    register_response = manager.auth_api.register_user(admin_data)

    assert register_response.json()["role"] == "ADMIN", (
        f"Инвайт-код не сработал, "
        f"роль {register_response.json()['role']}, проверь .env"
    )

    manager.auth_api.authenticate((admin_data.email, admin_data.password))

    yield manager

    session.close()


@pytest.fixture(scope="function")
def manager_manager():
    if not MANAGER_INVITE_CODE:
        pytest.skip("в .env нет INVITE_CODE_MANAGER")

    session = requests.Session()
    manager = ApiManager(session)

    manager_data = UserData.registration_data_manager()
    register_response = manager.auth_api.register_user(manager_data)

    assert register_response.json()["role"] == "MANAGER", (
        f"не сработал инвайт код,"
        f"роль {register_response.json()["role"]}, проверь .env"
    )

    manager.auth_api.authenticate((manager_data.email, manager_data.password))

    yield manager

    session.close()


@pytest.fixture(scope="function")
def db_guard(db):
    before_tests = db.product.count_all_products()
    yield before_tests
    after_tests = db.product.count_all_products()
    assert before_tests == after_tests, (
        "Количество строк в базе данных не совпало с тем, что было до тестов"
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
def created_review(api_manager, authenticated_user, created_product):
    review = ReviewData.create_full_review()

    leaved_review = api_manager.reviews_api.leave_review(created_product.id, review)
    extracted_review = ReviewResponse.model_validate(leaved_review.json())
    yield extracted_review


@pytest.fixture
def other_user():
    session = requests.Session()
    other_manager = ApiManager(session)

    user_data = UserData.registration_data()
    other_manager.auth_api.register_user(user_data)
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



@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright):
    playwright.selectors.set_test_id_attribute("data-testid")


@pytest.fixture
def ui_user(api_manager):
    registration = UserData.registration_data()

    api_manager.auth_api.register_user(registration)

    return registration


def _login_through_ui(page, user):
    """Вход через форму: одинаковый и для десктопа, и для телефона."""
    login_page = LoginPage(page).open()
    login_page.login(user.email, user.password)

    expect(login_page.header.profile_link).to_have_text(user.email)
    return page


@pytest.fixture
def logged_in_page(page, ui_user):
    """Вкладка браузера, в которой мы уже вошли в свой аккаунт."""
    return _login_through_ui(page, ui_user)


@pytest.fixture
def mobile_page(browser, playwright):
    """Тот же браузер, но притворяется телефоном: размер экрана, User-Agent, касания."""
    context = browser.new_context(**playwright.devices["iPhone 13"])
    page = context.new_page()

    yield page

    context.close()


@pytest.fixture
def logged_in_mobile_page(mobile_page, ui_user):
    return _login_through_ui(mobile_page, ui_user)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Упал тест в браузере - кладём в отчёт скриншот и адрес страницы."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    # у API-тестов страницы нет, у мобильных она называется иначе
    page = item.funcargs.get("mobile_page") or item.funcargs.get("page")
    if page is None:
        return

    allure.attach(
        page.screenshot(full_page=True),
        name="Скриншот в момент падения",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(page.url, name="Адрес страницы", attachment_type=allure.attachment_type.TEXT)