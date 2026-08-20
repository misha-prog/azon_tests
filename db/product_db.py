from db.db_client import DBClient


class ProductDB(DBClient):
    """База azon_product: каталог, корзины, отзывы."""

    def get_product(self, product_id):
        return self.fetch_one("SELECT * FROM products WHERE id = %s", (product_id,))

    def get_product_by_sku(self, sku):
        return self.fetch_one("SELECT * FROM products WHERE sku = %s", (sku,))

    def get_cart_items(self, user_id):
        # корзина и позиции лежат в разных таблицах - собираем их JOIN'ом
        return self.fetch_all(
            """
            SELECT ci.product_id, ci.quantity, ci.price_at_add, p.name
            FROM cart_items ci
            JOIN carts c ON c.id = ci.cart_id
            JOIN products p ON p.id = ci.product_id
            WHERE c.user_id = %s
            ORDER BY ci.added_at
            """,
            (user_id,),
        )

    def count_active_products(self, category_id):
        cnt = self.fetch_one(
            """
            SELECT count(*) AS total
            FROM products p
            WHERE p.deleted_at IS NULL
            AND p.category_id = %s
            """,
            (category_id,)
        )
        return cnt["total"]

    def count_all_products(self):
        cnt = self.fetch_one(
            """
            SELECT count(*) AS total
            FROM products p
            WHERE p.deleted_at IS NULL
            """
        )
        return cnt["total"]

    def top_5_products(self):
        return self.fetch_all(
            """
            SELECT count(r.id) AS reviews, round(avg(r.rating), 2) AS average_rating
            FROM products p
            JOIN reviews r ON r.product_id = p.id
            GROUP BY p.name
            ORDER BY reviews DESC, p.name
            LIMIT 5
            """
        )

    def product_reviews(self, product_id):
        return self.fetch_one(
            """
            SELECT count(r.id) AS reviews, round(avg(r.rating), 2) AS avg
            FROM products p
            JOIN reviews r ON r.product_id = p.id
            WHERE p.id = %s
            """,
            (product_id,)
        )

    def get_moderation_record(self, review_id):
        return self.fetch_one(
            """
                SELECT action, actor_user_id, payload
                FROM audit_log
                WHERE action = 'REVIEW_MODERATE_DELETE' AND entity_id = %s
                """,
            (str(review_id),),
        )

    def get_review_from_product(self, review_id):
        return self.fetch_one(
            """
            SELECT r.text, r.rating
            FROM reviews r
            WHERE r.id = %s
            """,
            (review_id,)
        )

    def count_reviews(self, product_id):
        cnt =  self.fetch_one(
            """
            SELECT count(r.id) AS total
            FROM products p
            JOIN reviews r ON r.product_id = p.id
            WHERE p.id = %s
            """,
            (product_id,)
        )
        return cnt["total"]