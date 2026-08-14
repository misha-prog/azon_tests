from utils.data_generator import DataGenerator
from models.products import ProductRequest

class ProductData:

    @staticmethod
    def create_full_product(category_id=None) -> ProductRequest:
        return ProductRequest(
            name = DataGenerator.generate_name_of_product(),
            sku = DataGenerator.generate_sku(),
            description = DataGenerator.generate_description(),
            price =  DataGenerator.generate_price(),
            stock =  DataGenerator.generate_stock(),
            category_id =  category_id,
        )

    @staticmethod
    def change_price() -> dict:
        return {"price": DataGenerator.generate_price()}

    @staticmethod
    def cart_item_data(product_id, quantity=None) -> dict:
        return {"product_id": str(product_id), "quantity": quantity}
