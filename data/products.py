from utils.data_generator import DataGenerator

class ProductData:

    @staticmethod
    def create_full_product() -> dict:
        return {
            "name": DataGenerator.generate_name_of_product(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": "",
        }

    @staticmethod
    def change_price() -> dict:
        return {"price": DataGenerator.generate_price()}
