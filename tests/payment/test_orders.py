class TestOrder:

    def test_new_user_has_no_orders(self, api_manager, registered_user, authenticated_user):
        api_manager.user_api.get_user_info()

        response = api_manager.payment_api.get_orders()

        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []