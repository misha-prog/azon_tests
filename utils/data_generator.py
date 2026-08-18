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

    @staticmethod
    def generate_text():
        return fake.text(max_nb_chars=2000)

    @staticmethod
    def generate_rating():
        return fake.random_int(min=1, max=5)

    @staticmethod
    def generate_or_none_text():
        a = fake.random_int(min=1, max=100)
        if a < 50:
            return fake.text(max_nb_chars=2000)
        else:
            return None

    @staticmethod
    def generate_or_none_rating():
        a = fake.random_int(min=1, max=100)
        if a < 50:
            return fake.random_int(min=1, max=5)
        else:
            return None