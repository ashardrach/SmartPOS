from database.db import db

class Customer:

    @staticmethod
    def create(name, phone="", email="",
               address="", notes=""):
        db.execute("""
            INSERT INTO customers
            (name, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, notes))
        return db.get_last_id()

    @staticmethod
    def get_all():
        return db.fetchall("""
            SELECT * FROM customers
            ORDER BY name ASC
        """)

    @staticmethod
    def get_by_id(customer_id):
        return db.fetchone("""
            SELECT * FROM customers WHERE id = ?
        """, (customer_id,))

    @staticmethod
    def search(keyword):
        keyword = "%" + keyword + "%"
        return db.fetchall("""
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY name ASC
        """, (keyword, keyword))

    @staticmethod
    def update(customer_id, name, phone,
               email, address, notes):
        db.execute("""
            UPDATE customers SET
                name = ?, phone = ?, email = ?,
                address = ?, notes = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (name, phone, email,
              address, notes, customer_id))

    @staticmethod
    def update_debt(customer_id, amount_change):
        db.execute("""
            UPDATE customers SET
                outstanding_debt = outstanding_debt + ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (amount_change, customer_id))

    @staticmethod
    def update_total_purchases(customer_id, amount):
        db.execute("""
            UPDATE customers SET
                total_purchases = total_purchases + ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (amount, customer_id))

    @staticmethod
    def get_purchase_history(customer_id):
        return db.fetchall("""
            SELECT s.*, COUNT(si.id) as item_count
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            WHERE s.customer_id = ?
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """, (customer_id,))

    @staticmethod
    def get_debtors():
        return db.fetchall("""
            SELECT * FROM customers
            WHERE outstanding_debt > 0
            ORDER BY outstanding_debt DESC
        """)

    @staticmethod
    def delete(customer_id):
        db.execute("""
            DELETE FROM customers WHERE id = ?
        """, (customer_id,))