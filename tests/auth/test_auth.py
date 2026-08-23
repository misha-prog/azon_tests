import pytest

from data.users import UserData
from models.users import TokenPairResponse

pytestmark = pytest.mark.auth


class TestAuth:
    @pytest.mark.smoke
    def test_register_and_login(self, api_manager):
        user_data = UserData.registration_data()

        register_response = api_manager.auth_api.register_user(user_data)
        assert register_response.json()["role"] == "USER"

        api_manager.auth_api.authenticate((user_data.email, user_data.password))

        me_response = api_manager.user_api.get_user_info()
        assert me_response.json()["email"] == user_data.email

    def test_register_with_existing_email(self, api_manager, registered_user):
        user_data = UserData.registration_data()
        user_data.email = registered_user.registration.email

        response = api_manager.auth_api.register_user(user_data, expected_status=409)
        assert response.json()["error"]["code"] == "EMAIL_EXISTS"

    def test_login_with_wrong_password(self, api_manager, registered_user):
        credentials = UserData.login_data(registered_user.registration)
        credentials.password = "definetly-wrong-password"

        response = api_manager.auth_api.login_user(credentials, expected_status=401)
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    def test_token_body(self, registered_user, api_manager):
        user_data = UserData.login_data(registered_user.registration)
        response = api_manager.auth_api.login_user(user_data)

        token = TokenPairResponse.model_validate(response.json())

        assert token.token_type == "bearer"
        assert token.expires_in == 43200
        assert len(token.access_token.split(".")) == 3
