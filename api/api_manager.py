from api.auth_api import AuthAPI
from api.cart_api import CartAPI
from api.categories_api import CategoriesAPI
from api.payment_api import PaymentAPI
from api.products_api import ProductsAPI
from api.reviews_api import ReviewsAPI
from api.user_api import UserAPI


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.products_api = ProductsAPI(session)
        self.payment_api = PaymentAPI(session)
        self.user_api = UserAPI(session)
        self.categories_api = CategoriesAPI(session)
        self.cart_api = CartAPI(session)
        self.reviews_api = ReviewsAPI(session)
