import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QComboBox,
    QSpinBox, QDoubleSpinBox, QDialog,
    QFormLayout, QMessageBox, QScrollArea,
    QGridLayout, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from models.product import Product
from models.customer import Customer
from models.sale import Sale
from database.db import db

class POSView(QWidget):

    def __init__(self):
        super().__init__()
        self.cart_items = []
        self.selected_customer = None
        self.build_ui()
        self.setup_shortcuts()

    def build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left — Product search and grid
        left = self.build_left_panel()
        layout.addWidget(left, 3)

        # Right — Cart and checkout
        right = self.build_right_panel()
        layout.addWidget(right, 2)

    def build_left_panel(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #0f0f1a; padding: 20px;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 10, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("🛒 Point of Sale")
        title.setObjectName("page_title")
        layout.addWidget(title)

        # Search bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍  Search product by name or barcode...")
        self.search_input.setObjectName("search_box")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                color: #e0e0e0;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        search_row.addWidget(self.search_input)

        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(150)
        self.category_combo.addItem("All Categories", 0)
        categories = Product.get_categories()
        for cat in categories:
            self.category_combo.addItem(cat["name"], cat["id"])
        self.category_combo.currentIndexChanged.connect(
            self.search_products)
        search_row.addWidget(self.category_combo)
        layout.addLayout(search_row)

        # Product grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f1a;
            }
        """)

        self.product_grid_widget = QWidget()
        self.product_grid = QGridLayout(self.product_grid_widget)
        self.product_grid.setSpacing(10)
        self.product_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.product_grid_widget)
        layout.addWidget(scroll)

        self.load_products()
        return widget

    def build_right_panel(self):
        widget = QFrame()
        widget.setObjectName("cart_widget")
        widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-left: 1px solid #2a2a4a;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Cart title
        cart_title = QLabel("🧾 Current Order")
        cart_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(cart_title)

        # Customer selector
        cust_row = QHBoxLayout()
        cust_label = QLabel("Customer:")
        cust_label.setStyleSheet("color: #6a6a8a; min-width: 75px;")
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("Walk-in Customer", None)
        customers = Customer.get_all()
        for c in customers:
            self.customer_combo.addItem(
                c["name"] + " - " + c["phone"], c["id"])
        self.customer_combo.currentIndexChanged.connect(
            self.on_customer_changed)
        cust_row.addWidget(cust_label)
        cust_row.addWidget(self.customer_combo)
        layout.addLayout(cust_row)

        # Divider
        div = QFrame()
        div.setObjectName("divider")
        div.setStyleSheet("background-color: #2a2a4a; max-height: 1px;")
        layout.addWidget(div)

        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "Product", "Price", "Qty", "Total", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed)
        self.cart_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed)
        self.cart_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed)
        self.cart_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(1, 100)
        self.cart_table.setColumnWidth(2, 70)
        self.cart_table.setColumnWidth(3, 100)
        self.cart_table.setColumnWidth(4, 35)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.cart_table)

        # Discount row
        disc_row = QHBoxLayout()
        disc_label = QLabel("Discount (GHS):")
        disc_label.setStyleSheet("color: #6a6a8a;")
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(99999)
        self.discount_input.setDecimals(2)
        self.discount_input.valueChanged.connect(self.update_totals)
        disc_row.addWidget(disc_label)
        disc_row.addStretch()
        disc_row.addWidget(self.discount_input)
        layout.addLayout(disc_row)

        # Totals
        div2 = QFrame()
        div2.setStyleSheet("background-color: #2a2a4a; max-height: 1px;")
        layout.addWidget(div2)

        totals_layout = QVBoxLayout()
        totals_layout.setSpacing(6)

        self.subtotal_label = self.make_total_row(
            totals_layout, "Subtotal:", "GHS 0.00")
        self.discount_label = self.make_total_row(
            totals_layout, "Discount:", "GHS 0.00")

        div3 = QFrame()
        div3.setStyleSheet("background-color: #2a2a4a; max-height: 1px;")
        totals_layout.addWidget(div3)

        total_row = QHBoxLayout()
        total_text = QLabel("TOTAL:")
        total_text.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #ffffff;")
        self.total_label = QLabel("GHS 0.00")
        self.total_label.setObjectName("cart_total_label")
        self.total_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #00c853;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(total_text)
        total_row.addWidget(self.total_label)
        totals_layout.addLayout(total_row)
        layout.addLayout(totals_layout)

        # Payment method
        pay_row = QHBoxLayout()
        pay_label = QLabel("Payment:")
        pay_label.setStyleSheet("color: #6a6a8a; min-width: 75px;")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "MoMo", "Credit"])
        self.payment_combo.currentTextChanged.connect(
            self.on_payment_changed)
        pay_row.addWidget(pay_label)
        pay_row.addWidget(self.payment_combo)
        layout.addLayout(pay_row)

        # Amount paid
        paid_row = QHBoxLayout()
        paid_label = QLabel("Amount Paid:")
        paid_label.setStyleSheet("color: #6a6a8a; min-width: 75px;")
        self.amount_paid_input = QDoubleSpinBox()
        self.amount_paid_input.setMinimum(0)
        self.amount_paid_input.setMaximum(999999)
        self.amount_paid_input.setDecimals(2)
        self.amount_paid_input.valueChanged.connect(self.update_change)
        paid_row.addWidget(paid_label)
        paid_row.addWidget(self.amount_paid_input)
        layout.addLayout(paid_row)

        # Change
        change_row = QHBoxLayout()
        change_text = QLabel("Change:")
        change_text.setStyleSheet("color: #6a6a8a; min-width: 75px;")
        self.change_label = QLabel("GHS 0.00")
        self.change_label.setStyleSheet(
            "color: #ffab40; font-weight: bold; font-size: 15px;")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        change_row.addWidget(change_text)
        change_row.addWidget(self.change_label)
        layout.addLayout(change_row)

        # MoMo reference (hidden by default)
        self.momo_input = QLineEdit()
        self.momo_input.setPlaceholderText("MoMo Reference Number...")
        self.momo_input.setVisible(False)
        layout.addWidget(self.momo_input)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setObjectName("btn_danger")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff1744;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff5252; }
        """)
        self.clear_btn.clicked.connect(self.clear_cart)

        self.checkout_btn = QPushButton("✅ Checkout  F5")
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #00c853;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00e676; }
            QPushButton:disabled {
                background-color: #2a2a4a;
                color: #5a5a7a;
            }
        """)
        self.checkout_btn.clicked.connect(self.process_checkout)
        self.checkout_btn.setEnabled(False)

        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.checkout_btn, 2)
        layout.addLayout(btn_row)

        return widget

    def make_total_row(self, parent_layout, label, value):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #6a6a8a;")
        val = QLabel(value)
        val.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        row.addWidget(lbl)
        row.addWidget(val)
        parent_layout.addLayout(row)
        return val

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self,
                  activated=self.process_checkout)
        QShortcut(QKeySequence("Escape"), self,
                  activated=self.clear_cart)
        QShortcut(QKeySequence("Ctrl+F"), self,
                  activated=lambda: self.search_input.setFocus())

    def load_products(self, keyword="", category_id=0):
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if keyword:
            products = Product.search(keyword)
        else:
            products = Product.get_all()

        if category_id:
            products = [p for p in products
                       if p["category_id"] == category_id]

        cols = 3
        for i, product in enumerate(products):
            card = self.make_product_card(product)
            self.product_grid.addWidget(card, i // cols, i % cols)

        if not products:
            empty = QLabel("No products found")
            empty.setStyleSheet("color: #6a6a8a; font-size: 14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.product_grid.addWidget(empty, 0, 0, 1, cols)

    def make_product_card(self, product):
        card = QPushButton()
        card.setObjectName("product_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        stock = product["stock_quantity"]
        stock_color = "#00c853" if stock > 10 else \
                      "#ffab40" if stock > 0 else "#ff1744"

        card.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px;
                text-align: left;
                min-height: 80px;
            }}
            QPushButton:hover {{
                border: 1px solid #4a9eff;
                background-color: #1e2040;
            }}
            QPushButton:pressed {{
                background-color: #2a2a5a;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        name = QLabel(product["name"][:25])
        name.setStyleSheet(
            "color: #e0e0e0; font-weight: bold; font-size: 12px;")
        name.setWordWrap(True)
        layout.addWidget(name)

        price = QLabel("GHS {:.2f}".format(product["selling_price"]))
        price.setStyleSheet(
            "color: #4a9eff; font-size: 14px; font-weight: bold;")
        layout.addWidget(price)

        stock_label = QLabel("Stock: " + str(stock))
        stock_label.setStyleSheet(
            f"color: {stock_color}; font-size: 11px;")
        layout.addWidget(stock_label)

        if stock == 0:
            card.setEnabled(False)
            card.setStyleSheet(card.styleSheet() + """
                QPushButton:disabled {
                    background-color: #0f0f1a;
                    border: 1px solid #1a1a2e;
                    opacity: 0.5;
                }
            """)

        card.clicked.connect(
            lambda checked, p=product: self.add_to_cart(p))
        return card

    def search_products(self):
        keyword = self.search_input.text().strip()
        cat_id = self.category_combo.currentData()
        self.load_products(keyword, cat_id or 0)

    def add_to_cart(self, product):
        for item in self.cart_items:
            if item["product_id"] == product["id"]:
                if item["quantity"] < product["stock_quantity"]:
                    item["quantity"] += 1
                    self.refresh_cart()
                else:
                    QMessageBox.warning(
                        self, "Stock Limit",
                        "Not enough stock available!")
                return

        self.cart_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "unit_price": product["selling_price"],
            "quantity": 1,
            "stock": product["stock_quantity"]
        })
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.setRowCount(len(self.cart_items))

        for row, item in enumerate(self.cart_items):
            self.cart_table.setItem(
                row, 0, QTableWidgetItem(item["name"][:20]))
            self.cart_table.setItem(
                row, 1, QTableWidgetItem(
                    "GHS {:.2f}".format(item["unit_price"])))

            qty_widget = QSpinBox()
            qty_widget.setMinimum(1)
            qty_widget.setMaximum(item["stock"])
            qty_widget.setValue(item["quantity"])
            qty_widget.setStyleSheet("""
                QSpinBox {
                    background-color: #2a2a4a;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
            """)
            qty_widget.valueChanged.connect(
                lambda val, r=row: self.update_qty(r, val))
            self.cart_table.setCellWidget(row, 2, qty_widget)

            subtotal = item["unit_price"] * item["quantity"]
            self.cart_table.setItem(
                row, 3, QTableWidgetItem(
                    "GHS {:.2f}".format(subtotal)))

            remove_btn = QPushButton("✕")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff1744;
                    color: white;
                    border-radius: 4px;
                    font-size: 12px;
                    padding: 2px;
                }
                QPushButton:hover { background-color: #ff5252; }
            """)
            remove_btn.clicked.connect(
                lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)

        self.update_totals()
        self.checkout_btn.setEnabled(len(self.cart_items) > 0)

    def update_qty(self, row, value):
        if row < len(self.cart_items):
            self.cart_items[row]["quantity"] = value
            subtotal = (self.cart_items[row]["unit_price"] * value)
            self.cart_table.setItem(
                row, 3,
                QTableWidgetItem("GHS {:.2f}".format(subtotal)))
            self.update_totals()

    def remove_from_cart(self, row):
        if row < len(self.cart_items):
            self.cart_items.pop(row)
            self.refresh_cart()

    def update_totals(self):
        subtotal = sum(
            item["unit_price"] * item["quantity"]
            for item in self.cart_items
        )
        discount = self.discount_input.value()
        total = max(0, subtotal - discount)

        self.subtotal_label.setText(
            "GHS {:.2f}".format(subtotal))
        self.discount_label.setText(
            "GHS {:.2f}".format(discount))
        self.total_label.setText(
            "GHS {:.2f}".format(total))

        self.amount_paid_input.setMinimum(total)
        if self.amount_paid_input.value() < total:
            self.amount_paid_input.setValue(total)

        self.update_change()

    def update_change(self):
        subtotal = sum(
            item["unit_price"] * item["quantity"]
            for item in self.cart_items
        )
        discount = self.discount_input.value()
        total = max(0, subtotal - discount)
        paid = self.amount_paid_input.value()
        change = max(0, paid - total)
        self.change_label.setText("GHS {:.2f}".format(change))

    def on_customer_changed(self):
        self.selected_customer = self.customer_combo.currentData()

    def on_payment_changed(self, method):
        self.momo_input.setVisible(method == "MoMo")

    def clear_cart(self):
        if self.cart_items:
            reply = QMessageBox.question(
                self, "Clear Cart",
                "Clear all items from cart?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.cart_items = []
                self.discount_input.setValue(0)
                self.refresh_cart()

    def process_checkout(self):
        if not self.cart_items:
            return

        subtotal = sum(
            item["unit_price"] * item["quantity"]
            for item in self.cart_items
        )
        discount = self.discount_input.value()
        total = max(0, subtotal - discount)
        amount_paid = self.amount_paid_input.value()
        payment_method = self.payment_combo.currentText().lower()
        momo_ref = self.momo_input.text().strip()

        if payment_method == "cash" and amount_paid < total:
            QMessageBox.warning(
                self, "Insufficient Payment",
                "Amount paid is less than total!")
            return

        try:
            sale_items = [{
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"]
            } for item in self.cart_items]

            sale_id = Sale.create(
                items=sale_items,
                payment_method=payment_method,
                amount_paid=amount_paid,
                customer_id=self.selected_customer,
                discount_amount=discount,
                momo_reference=momo_ref
            )

            change = max(0, amount_paid - total)

            msg = QMessageBox(self)
            msg.setWindowTitle("✅ Sale Complete!")
            msg.setText(
                f"<b>Sale #{sale_id} completed!</b><br><br>"
                f"Total: <b>GHS {total:.2f}</b><br>"
                f"Paid: <b>GHS {amount_paid:.2f}</b><br>"
                f"Change: <b>GHS {change:.2f}</b>"
            )
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a1a2e;
                    color: white;
                }
                QMessageBox QLabel { color: white; font-size: 14px; }
                QPushButton {
                    background-color: #00c853;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
            """)
            msg.exec()

            self.cart_items = []
            self.discount_input.setValue(0)
            self.momo_input.clear()
            self.refresh_cart()
            self.load_products()

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                "Sale failed: " + str(e))

    def refresh(self):
        self.load_products()
        self.customer_combo.clear()
        self.customer_combo.addItem("Walk-in Customer", None)
        customers = Customer.get_all()
        for c in customers:
            self.customer_combo.addItem(
                c["name"] + " - " + c["phone"], c["id"])