from database.db import db
from models.product import Product
from models.customer import Customer

class Sale:

    @staticmethod
    def create(items, payment_method="cash",
               amount_paid=0, customer_id=None,
               discount_amount=0, notes="",
               cashier_name="Admin",
               momo_reference=""):

        subtotal = sum(
            item["quantity"] * item["unit_price"]
            for item in items
        )
        total_amount = subtotal - discount_amount
        change_amount = max(0, amount_paid - total_amount)

        db.execute("""
            INSERT INTO sales
            (customer_id, cashier_name, subtotal,
             discount_amount, total_amount, amount_paid,
             change_amount, payment_method,
             momo_reference, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, cashier_name, subtotal,
              discount_amount, total_amount,
              amount_paid, change_amount,
              payment_method, momo_reference, notes))

        sale_id = db.get_last_id()

        for item in items:
            product = Product.get_by_id(item["product_id"])
            db.execute("""
                INSERT INTO sale_items
                (sale_id, product_id, product_name,
                 quantity, unit_price, cost_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sale_id,
                  item["product_id"],
                  product["name"],
                  item["quantity"],
                  item["unit_price"],
                  product.get("cost_price", 0),
                  item["quantity"] * item["unit_price"]))

            Product.update_stock(
                item["product_id"],
                -item["quantity"],
                "Sale #" + str(sale_id)
            )

        if customer_id:
            Customer.update_total_purchases(
                customer_id, total_amount)
            if payment_method == "credit":
                Customer.update_debt(
                    customer_id, total_amount)

        if payment_method == "momo":
            db.execute("""
                INSERT INTO momo_transactions
                (reference, amount, transaction_type,
                 sale_id, notes)
                VALUES (?, ?, 'incoming', ?, ?)
            """, (momo_reference, amount_paid,
                  sale_id, "Sale #" + str(sale_id)))

        return sale_id

    @staticmethod
    def get_by_id(sale_id):
        sale = db.fetchone("""
            SELECT s.*,
                   c.name as customer_name,
                   c.phone as customer_phone
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        """, (sale_id,))
        if sale:
            sale["items"] = db.fetchall("""
                SELECT * FROM sale_items
                WHERE sale_id = ?
            """, (sale_id,))
        return sale

    @staticmethod
    def get_today_sales():
        return db.fetchall("""
            SELECT s.*,
                   c.name as customer_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.created_at) = DATE('now')
            AND s.status = 'completed'
            ORDER BY s.created_at DESC
        """)

    @staticmethod
    def get_sales_by_date(start_date, end_date):
        return db.fetchall("""
            SELECT s.*,
                   c.name as customer_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.created_at) BETWEEN ? AND ?
            AND s.status = 'completed'
            ORDER BY s.created_at DESC
        """, (start_date, end_date))

    @staticmethod
    def get_daily_summary(date=None):
        if not date:
            date = "DATE('now')"
            params = ()
        else:
            date = "?"
            params = (date,)

        return db.fetchone(f"""
            SELECT
                COUNT(*) as total_transactions,
                SUM(total_amount) as total_revenue,
                SUM(discount_amount) as total_discounts,
                SUM(CASE WHEN payment_method='cash'
                    THEN total_amount ELSE 0 END) as cash_total,
                SUM(CASE WHEN payment_method='momo'
                    THEN total_amount ELSE 0 END) as momo_total,
                SUM(CASE WHEN payment_method='credit'
                    THEN total_amount ELSE 0 END) as credit_total,
                AVG(total_amount) as average_sale
            FROM sales
            WHERE DATE(created_at) = {date}
            AND status = 'completed'
        """, params)

    @staticmethod
    def get_profit_summary(start_date, end_date):
        return db.fetchone("""
            SELECT
                SUM(si.subtotal) as total_revenue,
                SUM(si.cost_price * si.quantity) as total_cost,
                SUM(si.subtotal -
                    (si.cost_price * si.quantity)) as total_profit,
                COUNT(DISTINCT s.id) as total_sales
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE DATE(s.created_at) BETWEEN ? AND ?
            AND s.status = 'completed'
        """, (start_date, end_date))

    @staticmethod
    def get_top_products(limit=10, days=30):
        return db.fetchall("""
            SELECT
                si.product_name,
                SUM(si.quantity) as total_sold,
                SUM(si.subtotal) as total_revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.created_at >= datetime('now', '-' || ? || ' days')
            AND s.status = 'completed'
            GROUP BY si.product_id
            ORDER BY total_sold DESC
            LIMIT ?
        """, (days, limit))

    @staticmethod
    def void_sale(sale_id):
        sale = Sale.get_by_id(sale_id)
        if not sale:
            return False
        for item in sale["items"]:
            Product.update_stock(
                item["product_id"],
                item["quantity"],
                "Void Sale #" + str(sale_id)
            )
        db.execute("""
            UPDATE sales SET status = 'voided'
            WHERE id = ?
        """, (sale_id,))
        return True