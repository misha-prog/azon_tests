from models.reviews import ReviewCreateRequest, ReviewUpdateRequest
from utils.data_generator import DataGenerator

class ReviewData:
    @staticmethod
    def create_full_review() -> ReviewCreateRequest:
        return ReviewCreateRequest(
            rating=DataGenerator.generate_rating(),
            text=DataGenerator.generate_text()
        )

    @staticmethod
    def update_review() -> ReviewUpdateRequest:
        while True:
            rating_none = DataGenerator.generate_or_none_rating()
            text_none = DataGenerator.generate_or_none_text()
            if rating_none is not None or text_none is not None:
                return ReviewUpdateRequest(
                    rating=rating_none,
                    text=text_none
                )

    @staticmethod
    def review_with_extra_field() -> dict:
        # намеренно словарь: модель с extra="forbid" такое просто не соберёт,
        # а проверить надо ответ сервиса
        return {"rating": 5, "text": "Пробуем лишнее поле", "user_id": "no-such-field"}
