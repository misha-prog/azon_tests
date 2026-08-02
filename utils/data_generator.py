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