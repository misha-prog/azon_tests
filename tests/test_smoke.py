import pytest

pytestmark = pytest.mark.smoke


class TestSmoke:
    @pytest.mark.parametrize(
        "client_name", ["auth_api", "user_api", "products_api", "payment_api"]
    )
    def test_health(self, api_manager, client_name):
        client = getattr(api_manager, client_name)

        response = client.get_health()

        assert response.json()["status"] == "ok"
