from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from models.users import LoginRequest, RegisterRequest
from utils.data_generator import DataGenerator


class UserData:
    @staticmethod
    def registration_data(invite_code=None) -> RegisterRequest:
        return RegisterRequest(
            email=DataGenerator.generate_email(),
            password=DataGenerator.generate_password(),
            full_name=DataGenerator.generate_full_name(),
            invite_code=invite_code,
        )

    @staticmethod
    def registration_data_admin() -> RegisterRequest:
        return RegisterRequest(
            email=DataGenerator.generate_email(),
            password=DataGenerator.generate_password(),
            full_name=DataGenerator.generate_full_name(),
            invite_code=ADMIN_INVITE_CODE,
        )

    @staticmethod
    def registration_data_manager() -> RegisterRequest:
        return RegisterRequest(
            email=DataGenerator.generate_email(),
            password=DataGenerator.generate_password(),
            full_name=DataGenerator.generate_full_name(),
            invite_code=MANAGER_INVITE_CODE,
        )

    @staticmethod
    def login_data(user_data) -> LoginRequest:
        if hasattr(user_data, "model_dump"):
            user_data = user_data.model_dump()

        return LoginRequest(email=user_data["email"], password=user_data["password"])

    @staticmethod
    def update_profile_data() -> dict:
        return {"full_name": DataGenerator.generate_full_name()}

    @staticmethod
    def change_password_data(user_data, new_password) -> dict:
        if hasattr(user_data, "model_dump"):
            user_data = user_data.model_dump()

        return {
            "old_password": user_data["password"],
            "new_password": new_password,
        }
