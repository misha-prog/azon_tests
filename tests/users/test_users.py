from tests.conftest import authenticated_user
from data.users import UserData

class TestUsers:

    def test_get_user_without_token(self, api_manager):
        response = api_manager.user_api.get_user_info(expected_status=401)

        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_get_user_info(self, api_manager, authenticated_user):
        user_data = authenticated_user
        check_user_data = api_manager.user_api.get_user_info()


        assert user_data["email"] == check_user_data.json()["email"]
        assert check_user_data.json()["role"] == "USER"

    def test_me_without_auth_returns_401(self, api_manager):
        response = api_manager.user_api.get_user_info(expected_status=401)
        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_update_full_name(self, api_manager, authenticated_user):
        new_name = UserData.update_profile_data()["full_name"]
        api_manager.user_api.update_user_info({"full_name": new_name})

        response = api_manager.user_api.get_user_info()
        assert response.json()["full_name"] == new_name

    def test_change_password(self, api_manager, authenticated_user):
        user_data = authenticated_user
        UserData.change_password_data(user_data, "aboba123")

        old_credentials = UserData.login_data(user_data)
        response = api_manager.auth_api.login_user(old_credentials, expected_status=401)
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

        api_manager.auth_api.authenticate((authenticated_user["email"], "aboba123"))