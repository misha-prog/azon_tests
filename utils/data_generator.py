import uuid

from faker import Faker

fake = Faker("en_US")

class DataGenerator:

    @staticmethod
    def generate_email():
        return f"student-{uuid.uuid4().hex[:8]}@test.com"

    @staticmethod
    def generate_password():
        return fake.password(length=12)

    @staticmethod
    def generate_full_name():
        return fake.name()

    @staticmethod
    def generate_name_of_product():
        return fake.word().capitalize()

    @staticmethod
    def generate_sku():
        return fake.password(length=19, special_chars=False, upper_case=True, lower_case=True)

    @staticmethod
    def generate_description():
        return fake.text(max_nb_chars=50)

    @staticmethod
    def generate_price():
        return fake.random_int(min=500, max=100000)

    @staticmethod
    def generate_stock():
        return fake.random_int(min=1, max=1000, step=10)