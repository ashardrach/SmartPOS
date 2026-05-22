from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QComboBox,
    QDialog, QFormLayout, QMessageBox,
    QSpinBox, QDoubleSpinBox, QTextEdit,
    QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.product import Product

class InventoryView(QWidget):

    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        left = QVBoxLayout()
        title = QLabel("📦 Inventory")
        title.setObjectName("page_title")
        subtitle = QLabel("Manage your products and stock levels")
        subtitle.setObjectName("page_subtitle")
        left.addWidget(title)
        left.addWidget(subtitle)
        header.addLayout(left)
        header.addStretch()

        add_btn = QPushButton("+ Add Product")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6ab0ff; }
        """)
        add_btn.clicked.connect(self.add_product)
        header.addWidget(add_btn)

        add_cat_btn = QPushButton("+ Add Category")
        add_cat_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #a0a0c0;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #3a3a5a; }
        """)
        add_cat_btn.clicked.connect(self.add_category)
        header.addWidget(add_cat_btn)
        layout.addLayout(header)

        # Stats row
        stats = QHBoxLayout()
        self.stat_total = self.make_stat("📦 Total Products", "0")
        self.stat_low = self.make_stat("⚠️ Low Stock", "0")
        self.stat_value = self.make_stat("💰 Stock Value", "GHS 0.00")
        for s in [self.stat_total, self.stat_low, self.stat_value]:
            stats.addWidget(s)
        stats.addStretch()
        layout.addLayout(stats)

        # Search and filter
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products...")
        self.search_input.textChanged.connect(self.load_products)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 15px;
                color: #e0e0e0;
                min-height: 36px;
            }
            QLineEdit:focus { border: 1px solid #4a9eff; }
        """)

        self.cat_filter = QComboBox()
        self.cat_filter.addItem("All Categories", 0)
        for cat in Product.get_categories():
            self.cat_filter.addItem(cat["name"], cat["id"])
        self.cat_filter.currentIndexChanged.connect(self.load_products)

        self.stock_filter = QComboBox()
        self.stock_filter.addItems([
            "All Stock", "Low Stock Only", "Out of Stock"])
        self.stock_filter.currentIndexChanged.connect(self.load_products)

        filter_row.addWidget(self.search_input, 2)
        filter_row.addWidget(self.cat_filter)
        filter_row.addWidget(self.stock_filter)
        layout.addLayout(filter_row)

        # Products table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Category",
            "Selling Price", "Cost Price",
            "Stock", "Min Stock", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 150)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.load_products()

    def make_stat(self, label, value):
        frame = QFrame()
        frame.setObjectName("stat_card")
        frame.setFixedHeight(70)
        frame.setFixedWidth(200)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        val = QLabel(value)
        val.setObjectName("stat_value")
        val.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a9eff;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        frame.value_label = val
        return frame

    def load_products(self):
        keyword = self.search_input.text().strip()
        cat_id = self.cat_filter.currentData()
        stock_filter = self.stock_filter.currentIndex()

        if keyword:
            products = Product.search(keyword)
        else:
            products = Product.get_all()

        if cat_id:
            products = [p for p in products
                       if p["category_id"] == cat_id]

        if stock_filter == 1:
            products = [p for p in products
                       if 0 < p["stock_quantity"] <=
                       p["low_stock_threshold"]]
        elif stock_filter == 2:
            products = [p for p in products
                       if p["stock_quantity"] == 0]

        self.table.setRowCount(len(products))

        total_value = 0
        low_count = 0

        for row, p in enumerate(products):
            self.table.setItem(
                row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(
                row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(
                row, 2, QTableWidgetItem(
                    p.get("category_name", "")))
            self.table.setItem(
                row, 3, QTableWidgetItem(
                    "GHS {:.2f}".format(p["selling_price"])))
            self.table.setItem(
                row, 4, QTableWidgetItem(
                    "GHS {:.2f}".format(p["cost_price"])))

            stock = p["stock_quantity"]
            stock_item = QTableWidgetItem(str(stock))
            if stock == 0:
                stock_item.setForeground(QColor("#ff1744"))
            elif stock <= p["low_stock_threshold"]:
                stock_item.setForeground(QColor("#ffab40"))
                low_count += 1
            else:
                stock_item.setForeground(QColor("#00c853"))
            self.table.setItem(row, 5, stock_item)

            self.table.setItem(
                row, 6, QTableWidgetItem(
                    str(p["low_stock_threshold"])))

            total_value += p["cost_price"] * stock

            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #6ab0ff; }
            """)
            edit_btn.clicked.connect(
                lambda checked, pid=p["id"]: self.edit_product(pid))

            restock_btn = QPushButton("Restock")
            restock_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00c853;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #00e676; }
            """)
            restock_btn.clicked.connect(
                lambda checked, pid=p["id"]: self.restock_product(pid))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(restock_btn)
            self.table.setCellWidget(row, 7, btn_widget)

        all_products = Product.get_all()
        self.stat_total.value_label.setText(str(len(all_products)))
        self.stat_low.value_label.setText(str(low_count))
        self.stat_value.value_label.setText(
            "GHS {:.2f}".format(total_value))

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            Product.create(**data)
            self.load_products()
            QMessageBox.information(
                self, "Success", "Product added successfully!")

    def edit_product(self, product_id):
        product = Product.get_by_id(product_id)
        if not product:
            return
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            Product.update(
                product_id,
                data["name"], data["selling_price"],
                data["cost_price"], data["stock_quantity"],
                data["category_id"], data["barcode"],
                data["unit"], data["low_stock_threshold"],
                data["description"]
            )
            self.load_products()

    def restock_product(self, product_id):
        product = Product.get_by_id(product_id)
        if not product:
            return
        dialog = RestockDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            qty = dialog.get_quantity()
            Product.update_stock(product_id, qty, "Manual restock")
            self.load_products()

    def add_category(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self, "Add Category", "Category name:")
        if ok and name.strip():
            Product.add_category(name.strip())
            self.cat_filter.clear()
            self.cat_filter.addItem("All Categories", 0)
            for cat in Product.get_categories():
                self.cat_filter.addItem(cat["name"], cat["id"])
            QMessageBox.information(
                self, "Success", "Category added!")

    def refresh(self):
        self.load_products()


class ProductDialog(QDialog):

    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(
            "Edit Product" if product else "Add New Product")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #e0e0e0; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 32px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4a9eff;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6ab0ff; }
        """)
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("GHS ")

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMaximum(999999)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("GHS ")

        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(999999)

        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(999999)
        self.min_stock_input.setValue(5)

        self.category_combo = QComboBox()
        for cat in Product.get_categories():
            self.category_combo.addItem(cat["name"], cat["id"])

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Optional barcode")

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g. piece, kg, litre")
        self.unit_input.setText("piece")

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText("Optional description")

        layout.addRow("Product Name *", self.name_input)
        layout.addRow("Selling Price *", self.price_input)
        layout.addRow("Cost Price", self.cost_input)
        layout.addRow("Stock Quantity", self.stock_input)
        layout.addRow("Min Stock Alert", self.min_stock_input)
        layout.addRow("Category", self.category_combo)
        layout.addRow("Barcode", self.barcode_input)
        layout.addRow("Unit", self.unit_input)
        layout.addRow("Description", self.desc_input)

        if self.product:
            self.name_input.setText(self.product["name"])
            self.price_input.setValue(self.product["selling_price"])
            self.cost_input.setValue(self.product["cost_price"])
            self.stock_input.setValue(self.product["stock_quantity"])
            self.min_stock_input.setValue(
                self.product["low_stock_threshold"])
            self.barcode_input.setText(self.product.get("barcode",""))
            self.unit_input.setText(self.product.get("unit","piece"))
            self.desc_input.setText(
                self.product.get("description",""))
            idx = self.category_combo.findData(
                self.product["category_id"])
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #a0a0c0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton(
            "Update Product" if self.product else "Add Product")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addRow("", btn_row)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "selling_price": self.price_input.value(),
            "cost_price": self.cost_input.value(),
            "stock_quantity": self.stock_input.value(),
            "low_stock_threshold": self.min_stock_input.value(),
            "category_id": self.category_combo.currentData(),
            "barcode": self.barcode_input.text().strip(),
            "unit": self.unit_input.text().strip(),
            "description": self.desc_input.toPlainText().strip()
        }


class RestockDialog(QDialog):

    def __init__(self, parent, product):
        super().__init__(parent)
        self.setWindowTitle("Restock: " + product["name"])
        self.setMinimumWidth(300)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #e0e0e0; }
            QSpinBox {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 36px;
                font-size: 16px;
            }
            QPushButton {
                background-color: #00c853;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        info = QLabel(
            "Current stock: <b style='color:#4a9eff'>" +
            str(product["stock_quantity"]) + "</b>")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        qty_label = QLabel("Add quantity:")
        qty_label.setStyleSheet("color: #a0a0c0;")
        layout.addWidget(qty_label)

        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(1)
        self.qty_input.setMaximum(99999)
        self.qty_input.setValue(10)
        layout.addWidget(self.qty_input)

        btn = QPushButton("✅ Add Stock")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_quantity(self):
        return self.qty_input.value()