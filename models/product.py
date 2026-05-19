from database.db import db
from datetime import datetime

class Product:

    @staticmethod
    def create(name, selling_price, cost_price=0,
                stock_quantity=0, category_id=1,
                barcode="", unit="piece",
                low_stock_threshold=5, description=""):
        db.execute("""
            INSERT INTO products
            (name, selling_price, cost_price, stock_quantity,
             category_id, barcode, unit,
             low_stock_threshold, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, selling_price, cost_price,
              stock_quantity, category_id, barcode,
              unit, low_stock_threshold, description))
        return db.get_last_id()

    @staticmethod
    def get_all(active_only=True):
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """
        if active_only:
            query += " WHERE p.is_active = 1"
        query += " ORDER BY p.name ASC"
        return db.fetchall(query)

    @staticmethod
    def get_by_id(product_id):
        return db.fetchone("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """, (product_id,))

    @staticmethod
    def get_by_barcode(barcode):
        return db.fetchone("""
            SELECT * FROM products
            WHERE barcode = ? AND is_active = 1
        """, (barcode,))

    @staticmethod
    def search(keyword):
        keyword = "%" + keyword + "%"
        return db.fetchall("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (p.name LIKE ? OR p.barcode LIKE ?)
            AND p.is_active = 1
            ORDER BY p.name ASC
        """, (keyword, keyword))

    @staticmethod
    def update(product_id, name, selling_price,
               cost_price, stock_quantity, category_id,
               barcode, unit, low_stock_threshold,
               description):
        db.execute("""
            UPDATE products SET
                name = ?, selling_price = ?,
                cost_price = ?, stock_quantity = ?,
                category_id = ?, barcode = ?,
                unit = ?, low_stock_threshold = ?,
                description = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (name, selling_price, cost_price,
              stock_quantity, category_id, barcode,
              unit, low_stock_threshold,
              description, product_id))

    @staticmethod
    def update_stock(product_id, quantity_change, notes=""):
        product = Product.get_by_id(product_id)
        if not product:
            return False
        previous = product["stock_quantity"]
        new_stock = previous + quantity_change
        if new_stock < 0:
            new_stock = 0
        db.execute("""
            UPDATE products SET
                stock_quantity = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (new_stock, product_id))
        db.execute("""
            INSERT INTO stock_movements
            (product_id, movement_type, quantity,
             previous_stock, new_stock, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id,
              "sale" if quantity_change < 0 else "restock",
              abs(quantity_change),
              previous, new_stock, notes))
        return new_stock

    @staticmethod
    def get_low_stock():
        return db.fetchall("""
            SELECT * FROM products
            WHERE stock_quantity <= low_stock_threshold
            AND is_active = 1
            ORDER BY stock_quantity ASC
        """)

    @staticmethod
    def delete(product_id):
        db.execute("""
            UPDATE products SET is_active = 0
            WHERE id = ?
        """, (product_id,))

    @staticmethod
    def get_categories():
        return db.fetchall("""
            SELECT * FROM categories ORDER BY name ASC
        """)

    @staticmethod
    def add_category(name, description=""):
        db.execute("""
            INSERT OR IGNORE INTO categories (name, description)
            VALUES (?, ?)
        """, (name, description))
        return db.get_last_id()