from models.orders import CardBody
from utils.data_generator import DataGenerator


SUCCESS_CARD_NUMBER = "4242424242424242"
DECLINED_CARD_NUMBER = "4000000000000002"
GATEWAY_CARD_NUMBER = "4000000000000119"
SLOW_CARD_NUMBER = "4000000000003220"
INSUFFICIENT_FUNDS_CARD_NUMBER = "4000000000009995"
EXPIRED_CARD_NUMBER = "4000000000000069"
INCORRECT_CVC_CARD_NUMBER = "4000000000000127"


class OrdersData:
    @staticmethod
    def valid_card(card_number: str) -> CardBody:
        return CardBody(
            card_number=card_number,
            card_holder=DataGenerator.generate_holder_name(),
            exp_month=DataGenerator.generate_exp_month(),
            exp_year=DataGenerator.generate_exp_year(),
            cvc=DataGenerator.generate_cvc(),
        )

    @classmethod
    def success_card(cls) -> CardBody:
        return cls.valid_card(SUCCESS_CARD_NUMBER)

    @classmethod
    def declined_card(cls) -> CardBody:
        return cls.valid_card(DECLINED_CARD_NUMBER)

    @classmethod
    def gateway_card(cls) -> CardBody:
        return cls.valid_card(GATEWAY_CARD_NUMBER)

    @classmethod
    def slow_card(cls) -> CardBody:
        return cls.valid_card(SLOW_CARD_NUMBER)

    @classmethod
    def insufficient_funds_card(cls) -> CardBody:
        return cls.valid_card(INSUFFICIENT_FUNDS_CARD_NUMBER)

    @classmethod
    def expired_card(cls) -> CardBody:
        return cls.valid_card(EXPIRED_CARD_NUMBER)

    @classmethod
    def incorrect_cvc_card(cls) -> CardBody:
        return cls.valid_card(INCORRECT_CVC_CARD_NUMBER)