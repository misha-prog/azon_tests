import requests
import pytest


from api.api_manager import ApiManager
from data.users import UserData


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