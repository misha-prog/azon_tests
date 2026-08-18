import pytest
import requests

from api.auth_api import AuthAPI
from api.user_api import UserAPI
from tests.mocks.stubs import AuthStubs
from utils.data_generator import DataGenerator

pytestmark = [pytest.mark.mock, pytest.mark.users]

def fake_creds():
    return {"email": DataGenerator.generate_email(), "password": DataGenerator.generate_password()}

def fake_user_data():
    return {"full_name": DataGenerator.generate_full_name()}

def test_count_of_calls_test_token(wiremock):
    session = requests.Session()
    wiremock.add_stub(AuthStubs.get_test_token())

    creds = fake_creds()
    AuthAPI(session, "http://localhost:8090").authenticate((creds["email"], creds["password"]))

    wiremock.add_stub(AuthStubs.get_patch_status())
    wiremock.add_stub(AuthStubs.get_user_info_status())

    UserAPI(session, "http://localhost:8090").get_user_info()
    UserAPI(session, "http://localhost:8090").update_user_info(fake_user_data())

    count_of_calls = {
        "urlPath": "/api/v1/users/me",
        "headers": {"Authorization": {"equalTo": "Bearer test-token"}},
    }

    assert wiremock.count_requests(count_of_calls) == 2

    response = wiremock.find_requests({
        "method": "POST",
        "urlPath": "/api/v1/auth/login"
    })[0]

    assert creds["password"] in response["body"]
    assert creds["password"] not in response["absoluteUrl"]
    assert creds["password"] not in str(response["headers"])