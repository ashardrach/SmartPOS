from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGridLayout,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models.sale import Sale
from models.product import Product
from models.customer import Customer
from database.db import db

class DashboardView(QWidget):

    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("page_title")
        subtitle = QLabel("Welcome back! Here's what's happening today.")
        subtitle.setObjectName("page_subtitle")
        header_left = QVBoxLayout()
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        header.addLayout(header_left)
        header.addStretch()
        layout.addLayout(header)

        # Stat cards
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(15)

        self.card_revenue = self.make_card(
            "💰", "Today's Revenue", "GHS 0.00", "blue")
        self.card_sales = self.make_card(
            "🛒", "Transactions", "0", "")
        self.card_products = self.make_card(
            "📦", "Total Products", "0", "")
        self.card_low_stock = self.make_card(
            "⚠️", "Low Stock Alerts", "0", "")
        self.card_customers = self.make_card(
            "👥", "Total Customers", "0", "")

        for card in [self.card_revenue, self.card_sales,
                     self.card_products, self.card_low_stock,
                     self.card_customers]:
            self.cards_layout.addWidget(card)

        layout.addLayout(self.cards_layout)

        # Bottom section
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        # Recent sales table
        sales_section = QVBoxLayout()
        sales_title = QLabel("Recent Sales")
        sales_title.setObjectName("label_primary")
        sales_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 10px;")
        sales_section.addWidget(sales_title)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            "ID", "Customer", "Total", "Payment", "Time"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        sales_section.addWidget(self.sales_table)
        bottom.addLayout(sales_section, 2)

        # Low stock section
        stock_section = QVBoxLayout()
        stock_title = QLabel("⚠️ Low Stock Items")
        stock_title.setObjectName("label_danger")
        stock_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 10px;")
        stock_section.addWidget(stock_title)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels([
            "Product", "Stock", "Min"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.verticalHeader().setVisible(False)
        self.stock_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        stock_section.addWidget(self.stock_table)
        bottom.addLayout(stock_section, 1)

        layout.addLayout(bottom)
        self.refresh()

    def make_card(self, icon, label, value, style=""):
        card = QFrame()
        card.setObjectName(
            "stat_card_blue" if style == "blue" else "stat_card"
        )
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        icon_label = QLabel(icon + "  " + label)
        icon_label.setObjectName("stat_label")
        layout.addWidget(icon_label)

        val_label = QLabel(value)
        val_label.setObjectName("stat_value")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        val_label.setFont(font)
        layout.addWidget(val_label)

        card.value_label = val_label
        return card

    def refresh(self):
        summary = Sale.get_daily_summary()
        products = Product.get_all()
        low_stock = Product.get_low_stock()
        customers = Customer.get_all()
        recent_sales = Sale.get_today_sales()

        revenue = summary["total_revenue"] or 0
        transactions = summary["total_transactions"] or 0

        self.card_revenue.value_label.setText(
            "GHS {:.2f}".format(revenue))
        self.card_sales.value_label.setText(str(transactions))
        self.card_products.value_label.setText(str(len(products)))
        self.card_low_stock.value_label.setText(str(len(low_stock)))
        self.card_customers.value_label.setText(str(len(customers)))

        # Recent sales
        self.sales_table.setRowCount(len(recent_sales[:10]))
        for row, sale in enumerate(recent_sales[:10]):
            self.sales_table.setItem(
                row, 0, QTableWidgetItem(str(sale["id"])))
            self.sales_table.setItem(
                row, 1, QTableWidgetItem(
                    sale.get("customer_name") or "Walk-in"))
            self.sales_table.setItem(
                row, 2, QTableWidgetItem(
                    "GHS {:.2f}".format(sale["total_amount"])))
            self.sales_table.setItem(
                row, 3, QTableWidgetItem(
                    sale["payment_method"].upper()))
            time_str = sale["created_at"][11:16]
            self.sales_table.setItem(
                row, 4, QTableWidgetItem(time_str))

        # Low stock
        self.stock_table.setRowCount(len(low_stock[:10]))
        for row, item in enumerate(low_stock[:10]):
            self.stock_table.setItem(
                row, 0, QTableWidgetItem(item["name"]))
            stock_item = QTableWidgetItem(
                str(item["stock_quantity"]))
            stock_item.setForeground(
                __import__('PyQt6.QtGui', fromlist=['QColor']).QColor("#ff1744"))
            self.stock_table.setItem(row, 1, stock_item)
            self.stock_table.setItem(
                row, 2, QTableWidgetItem(
                    str(item["low_stock_threshold"])))