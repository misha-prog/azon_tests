from utils.data_generator import DataGenerator

class UserData:

    @staticmethod
    def registration_data() -> dict:
        return {
            "email": DataGenerator.generate_email(),
            "password": DataGenerator.generate_password(),
            "full_name": DataGenerator.generate_full_name(),
        }

    @staticmethod
    def login_data(user_data) -> dict:
        return {"email": user_data["email"], "password": user_data["password"]}

    @staticmethod
    def update_profile_data() -> dict:
        return {"full_name": DataGenerator.generate_full_name()}

    @staticmethod
    def change_password_data(user_data, new_password) -> dict:
        return {"old_password": user_data["password"], "new_password": new_password}