import json
import logging

from pydantic import BaseModel

DEFAULT_TIMEOUT = 10

logger = logging.getLogger("azon_tests")
SECRET_FIELDS = {"password", "old_password", "new_password", "invite_code"}


class CustomRequester:
    """Базовый класс всех API-клиентов: отправка запросов и проверка статуса."""

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def send_request(self, method, endpoint, expected_status=200, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)

        if isinstance(kwargs.get("json"), BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(mode="json", exclude_none=True)

        response = self.session.request(method, url, **kwargs)
        self._log_request_and_response(response)

        if response.status_code != expected_status:
            raise AssertionError(
                f"{method} {url}: ожидали статус {expected_status}, "
                f"получили {response.status_code}. Тело ответа: {response.text}."
            )
        return response

    def _update_session_headers(self, **headers):
        self.session.headers.update(headers)

    def _mask_without_secrets(self, body):
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")

        try:
            payload = json.loads(body) if isinstance(body, str) else body
        except (json.JSONDecodeError, TypeError):
            return str(body)

        return json.dumps(self._mask_value(payload), ensure_ascii=False)

    def _mask_value(self, value):
        if isinstance(value, dict):
            return {
                key: "***"
                if str(key).lower() in SECRET_FIELDS
                else self._mask_value(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._mask_value(item) for item in value]
        return value

    def _log_request_and_response(self, response):
        request = response.request
        logger.info("--> %s %s", request.method, request.url)

        if request.body:
            masked_body = self._mask_without_secrets(request.body)
            logger.info("     тело запроса: %s", masked_body)
        logger.info(
            "<-- %s за %.2f c: %s",
            response.status_code,
            response.elapsed.total_seconds(),
            response.text[:500],
        )

    def get_health(self):
        return self.send_request("GET", "/health", expected_status=200)
