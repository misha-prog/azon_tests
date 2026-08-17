import uuid

PRODUCTS_ENDPOINT = "/api/v1/products"
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