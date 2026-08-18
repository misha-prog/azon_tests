import uuid

PRODUCTS_ENDPOINT = "/api/v1/products"
AUTH_ENDPOINT = "/api/v1/auth"
USERS_ENDPOINT = "/api/v1/users"
JSON_HEADERS = {"Content-Type": "application/json"}


def product_body(product_id, **overrides):
    """Тело товара ровно в том виде, в каком его отдаёт AZON."""
    body = {
        "id": product_id,
        "sku": "MOCK-0001",
        "name": "Умные часы AZON Watch 5",
        "description": "GPS, пульсоксиметр, 7 дней без подзарядки.",
        "price": "19990.00",
        "stock": 10,
        "category_id": "4ca772c1-bdb7-5e5f-9987-16fe30e499c8",
        "image_url": None,
        "rating_avg": 4.67,
        "reviews_count": 3,
        "is_seed": False,
        "is_available": True,
        "created_at": "2026-08-06T12:00:00Z",
        "updated_at": "2026-08-06T12:00:00Z",
    }
    return {**body, **overrides}


def error_body(code, message):
    """Тело ошибки AZON - тот самый формат, по коду которого мы ассертим с Темы 8."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": [],
            "request_id": "00000000-0000-0000-0000-000000000000",
        }
    }


def body_of_test_token():
    return {
        "access_token": "test-token",
        "refresh_token": "test-token",
        "token_type": "bearer",
        "expire_in": 43200
    }

def resp_of_upd():
    return {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "string",
      "full_name": "string",
      "phone": "string",
      "role": "USER",
      "is_active": True,
      "created_at": "2026-08-17T05:22:55.027Z"
}


class ProductStubs:
    """Стабы Product API: метод возвращает готовый мэппинг для WireMock."""

    @staticmethod
    def product_found(product_id, body=None):
        return {
            "request": {"method": "GET", "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}"},
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": body or product_body(product_id),
            },
        }

    @staticmethod
    def product_not_found(product_id):
        return {
            "request": {"method": "GET", "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}"},
            "response": {
                "status": 404,
                "headers": JSON_HEADERS,
                "jsonBody": error_body("PRODUCT_NOT_FOUND", "Product not found"),
            },
        }

    @staticmethod
    def product_page_and_size():
        return {
            "request": {
                "method": "GET",
                "urlPath": PRODUCTS_ENDPOINT,
                "queryParameters": {
                    "page": {"equalTo": "1"},
                    "size": {"equalTo": "2"}
                },
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": {
                    "items": [product_body(str(uuid.uuid4())), product_body(str(uuid.uuid4()), price="1000")],
                    "total": 2,
                    "page": 1,
                    "size": 2,
                    "pages": 1
                },
            },
        }


    @staticmethod
    def bad_gateway(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}"
            },

            "response": {
                "status": 503,
                "headers": JSON_HEADERS,
                "jsonBody": error_body("GATEWAY_ERROR", "technical timeout")
            },
        }

    @staticmethod
    def timeout_on_response(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },

            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": product_body(product_id),
                "fixedDelayMilliseconds": 5000,
            },
        }


    @staticmethod
    def product_lifecycle(product_id):
        # 1. пока сценарий в состоянии Started - товар есть
        a = {"scenarioName": "Жизнь товара",
         "requiredScenarioState": "Started",
         "request": {"method": "GET", "urlPath": f"/api/v1/products/{product_id}"},
         "response": {"status": 200, "jsonBody": {"id": f"{product_id}", "is_available": True}}}

        # 2. DELETE отвечает 204 и переводит сценарий в новое состояние
        b = {"scenarioName": "Жизнь товара",
         "requiredScenarioState": "Started",
         "newScenarioState": "Товар удалён",
         "request": {"method": "DELETE", "urlPath": f"/api/v1/products/{product_id}"},
         "response": {"status": 204}}

        # 3. в новом состоянии тот же GET отвечает уже 404
        c = {"scenarioName": "Жизнь товара",
         "requiredScenarioState": "Товар удалён",
         "request": {"method": "GET", "urlPath": f"/api/v1/products/{product_id}"},
         "response": {"status": 404, "jsonBody": {"error": {"code": "PRODUCT_NOT_FOUND"}}}}
        return [a,b,c]

class AuthStubs:

    @staticmethod
    def get_test_token():
        return {
            "request": {
                "method": "POST",
                "urlPath": f"{AUTH_ENDPOINT}/login",
            },
            "response": {
                "status": 200,
                "jsonBody": body_of_test_token(),
            }
        }

    @staticmethod
    def get_patch_status():
        return {
            "request": {
                "method": "PATCH",
                "urlPath": f"{USERS_ENDPOINT}/me",
            },
            "response": {
                "status": 200,
                "jsonBody": resp_of_upd(),
            },
        }

    @staticmethod
    def get_user_info_status():
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{USERS_ENDPOINT}/me",
            },
            "response": {
                "status": 200,
                "jsonBody": resp_of_upd(),
            },
        }