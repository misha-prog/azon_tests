from data.users import UserData
from tests.conftest import registered_user


class TestAuth:

    def test_register_and_login(self, api_manager):
        user_data = UserData.registration_data()

        register_response = api_manager.auth_api.register_user(user_data)
        assert register_response.json()["role"] == "USER"

        api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))

        me_response = api_manager.auth_api.get_me()
        assert me_response.json()["email"] == user_data["email"]

    def test_register_with_existing_email(self, api_manager, registered_user):
        user_data = UserData.registration_data()
        user_data["email"] = registered_user["email"]

        response = api_manager.auth_api.register_user(user_data, expected_status=409)
        assert response.json()["error"]["code"] == "EMAIL_EXISTS"

    def test_login_with_wrong_password(self, api_manager, registered_user):
        credentials = UserData.login_data(registered_user)
        credentials["password"] = "definetly-wrong-password"

        response = api_manager.auth_api.login_user(credentials, expected_status=401)
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
