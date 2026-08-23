import json
from unittest.mock import MagicMock

import pytest

from api.user_api import UserAPI
from config.hosts import AUTH_URL
from data.users import UserData

pytestmark = [pytest.mark.mock, pytest.mark.users]


def fake_response(status_code, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.elapsed.total_seconds.return_value = 0.01
    response.request.method = "POST"
    response.request.url = f"{AUTH_URL}/api/v1/users/me/password"
    response.request.body = None
    return response


def passwords_data():
    return UserData.change_password_data(UserData.registration_data(), "NewSecret123")


def test_change_password_need_1_post():
    session = MagicMock()
    session.request.return_value = fake_response(204)
    passwords = passwords_data()

    UserAPI(session).change_password(passwords)

    session.request.assert_called_once_with(
        "POST",
        f"{AUTH_URL}/api/v1/users/me/password",
        json={
            "old_password": passwords["old_password"],
            "new_password": passwords["new_password"],
        },
        timeout=10,
    )


def test_change_password_has_error():
    session = MagicMock()
    session.request.return_value = fake_response(400, '{"error": {"code": "WRONG_OLD_PASSWORD"}}')
    session.headers = {}

    with pytest.raises(AssertionError) as error:
        UserAPI(session).change_password(passwords_data())

    assert "ожидали статус 204, получили 400" in str(error.value)
    assert "WRONG_OLD_PASSWORD" in str(error.value)


def test_secret_fields_are_masked_without_changing_payload():
    session = MagicMock()
    requester = UserAPI(session)
    payload = {
        "password": "plain-password",
        "profile": {
            "old_password": "old-password",
            "new_password": "new-password",
            "invite_code": "invite-code",
        },
    }
    encoded_payload = json.dumps(payload)

    masked = json.loads(requester._mask_without_secrets(encoded_payload))

    assert masked == {
        "password": "***",
        "profile": {
            "old_password": "***",
            "new_password": "***",
            "invite_code": "***",
        },
    }
    assert json.loads(encoded_payload) == payload
