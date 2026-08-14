import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
conninfo = f"host=db.azon.130-17-2-195.sslip.io port=5432 user=student password={db_password} dbname=azon_product"

with psycopg.connect(conninfo) as connection:
    result = connection.execute("SELECT sku, price FROM products WHERE sku = %s", ("EL-002",))
    print(result.fetchone())

with psycopg.connect(conninfo, row_factory=dict_row) as connection:
    row = connection.execute("SELECT * FROM products WHERE sku = %s", ("EL-002",)).fetchone()
    print(row)
    print(row["name"], row["price"])