import os

import psycopg
from psycopg.rows import dict_row

from config.db import PRODUCT_DB, conninfo


def main():
    configured_sku = os.getenv("PRODUCT_SKU")

    with psycopg.connect(conninfo(PRODUCT_DB), row_factory=dict_row) as connection:
        if configured_sku:
            sku = configured_sku
        else:
            latest_product = connection.execute(
                "SELECT sku FROM products ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            if latest_product is None:
                raise RuntimeError("В таблице products нет товаров")
            sku = latest_product["sku"]

        row = connection.execute(
            "SELECT * FROM products WHERE sku = %s", (sku,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Товар с SKU {sku!r} не найден")

        print(row)
        print(row["name"], row["price"])


if __name__ == "__main__":
    main()
