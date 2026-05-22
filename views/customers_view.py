from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout,
    QMessageBox, QTextEdit, QFrame,
    QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.customer import Customer
from models.sale import Sale

class CustomersView(QWidget):

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
        title = QLabel("👥 Customers")
        title.setObjectName("page_title")
        subtitle = QLabel("Manage customer records and debt tracking")
        subtitle.setObjectName("page_subtitle")
        left.addWidget(title)
        left.addWidget(subtitle)
        header.addLayout(left)
        header.addStretch()

        add_btn = QPushButton("+ Add Customer")
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
        add_btn.clicked.connect(self.add_customer)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Stats
        stats = QHBoxLayout()
        self.stat_total = self.make_stat("👥 Total Customers", "0")
        self.stat_debt = self.make_stat("💸 Total Debt", "GHS 0.00")
        self.stat_debtors = self.make_stat("⚠️ Debtors", "0")
        for s in [self.stat_total, self.stat_debt,
                  self.stat_debtors]:
            stats.addWidget(s)
        stats.addStretch()
        layout.addLayout(stats)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #1a1a2e;
                color: #6a6a8a;
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #4a9eff;
                border-bottom: 2px solid #4a9eff;
            }
        """)

        # All customers tab
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)
        all_layout.setContentsMargins(10, 10, 10, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search customers...")
        self.search_input.textChanged.connect(self.load_customers)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 15px;
                color: #e0e0e0;
                min-height: 36px;
                margin-bottom: 10px;
            }
            QLineEdit:focus { border: 1px solid #4a9eff; }
        """)
        all_layout.addWidget(self.search_input)

        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email",
            "Total Purchases", "Debt", "Actions"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.customers_table.setColumnWidth(0, 50)
        self.customers_table.setColumnWidth(2, 130)
        self.customers_table.setColumnWidth(3, 180)
        self.customers_table.setColumnWidth(4, 130)
        self.customers_table.setColumnWidth(5, 100)
        self.customers_table.setColumnWidth(6, 160)
        self.customers_table.verticalHeader().setVisible(False)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.customers_table.doubleClicked.connect(
            self.view_customer)
        all_layout.addWidget(self.customers_table)
        tabs.addTab(all_tab, "All Customers")

        # Debtors tab
        debt_tab = QWidget()
        debt_layout = QVBoxLayout(debt_tab)
        debt_layout.setContentsMargins(10, 10, 10, 10)

        debt_info = QLabel(
            "⚠️  Customers with outstanding balances")
        debt_info.setStyleSheet(
            "color: #ffab40; font-size: 13px; margin-bottom: 8px;")
        debt_layout.addWidget(debt_info)

        self.debtors_table = QTableWidget()
        self.debtors_table.setColumnCount(5)
        self.debtors_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Total Purchases",
            "Debt Amount", "Actions"
        ])
        self.debtors_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.debtors_table.setColumnWidth(1, 130)
        self.debtors_table.setColumnWidth(2, 130)
        self.debtors_table.setColumnWidth(3, 120)
        self.debtors_table.setColumnWidth(4, 150)
        self.debtors_table.verticalHeader().setVisible(False)
        self.debtors_table.setAlternatingRowColors(True)
        self.debtors_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        debt_layout.addWidget(self.debtors_table)
        tabs.addTab(debt_tab, "💸 Debtors")

        layout.addWidget(tabs)
        self.load_customers()
        self.load_debtors()

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
        val.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #4a9eff;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        frame.value_label = val
        return frame

    def load_customers(self):
        keyword = self.search_input.text().strip()
        if keyword:
            customers = Customer.search(keyword)
        else:
            customers = Customer.get_all()

        self.customers_table.setRowCount(len(customers))
        total_debt = 0
        debtor_count = 0

        for row, c in enumerate(customers):
            self.customers_table.setItem(
                row, 0, QTableWidgetItem(str(c["id"])))
            self.customers_table.setItem(
                row, 1, QTableWidgetItem(c["name"]))
            self.customers_table.setItem(
                row, 2, QTableWidgetItem(c["phone"]))
            self.customers_table.setItem(
                row, 3, QTableWidgetItem(c.get("email", "")))
            self.customers_table.setItem(
                row, 4, QTableWidgetItem(
                    "GHS {:.2f}".format(c["total_purchases"])))

            debt = c["outstanding_debt"]
            debt_item = QTableWidgetItem(
                "GHS {:.2f}".format(debt))
            if debt > 0:
                debt_item.setForeground(QColor("#ff1744"))
                debtor_count += 1
                total_debt += debt
            else:
                debt_item.setForeground(QColor("#00c853"))
            self.customers_table.setItem(row, 5, debt_item)

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)

            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
            """)
            view_btn.clicked.connect(
                lambda checked, cid=c["id"]: self.view_customer_by_id(cid))

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a4a;
                    color: #a0a0c0;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
            """)
            edit_btn.clicked.connect(
                lambda checked, cid=c["id"]: self.edit_customer(cid))

            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
            self.customers_table.setCellWidget(row, 6, btn_widget)

        self.stat_total.value_label.setText(str(len(customers)))
        self.stat_debt.value_label.setText(
            "GHS {:.2f}".format(total_debt))
        self.stat_debtors.value_label.setText(str(debtor_count))

    def load_debtors(self):
        debtors = Customer.get_debtors()
        self.debtors_table.setRowCount(len(debtors))

        for row, c in enumerate(debtors):
            self.debtors_table.setItem(
                row, 0, QTableWidgetItem(c["name"]))
            self.debtors_table.setItem(
                row, 1, QTableWidgetItem(c["phone"]))
            self.debtors_table.setItem(
                row, 2, QTableWidgetItem(
                    "GHS {:.2f}".format(c["total_purchases"])))

            debt_item = QTableWidgetItem(
                "GHS {:.2f}".format(c["outstanding_debt"]))
            debt_item.setForeground(QColor("#ff1744"))
            self.debtors_table.setItem(row, 3, debt_item)

            pay_btn = QPushButton("Record Payment")
            pay_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00c853;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            pay_btn.clicked.connect(
                lambda checked, cid=c["id"],
                debt=c["outstanding_debt"]:
                self.record_payment(cid, debt))
            self.debtors_table.setCellWidget(row, 4, pay_btn)

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            Customer.create(**data)
            self.load_customers()
            self.load_debtors()

    def edit_customer(self, customer_id):
        customer = Customer.get_by_id(customer_id)
        if not customer:
            return
        dialog = CustomerDialog(self, customer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            Customer.update(
                customer_id,
                data["name"], data["phone"],
                data["email"], data["address"],
                data["notes"]
            )
            self.load_customers()

    def view_customer_by_id(self, customer_id):
        customer = Customer.get_by_id(customer_id)
        if customer:
            self.show_customer_detail(customer)

    def view_customer(self, index):
        row = index.row()
        customer_id = int(
            self.customers_table.item(row, 0).text())
        customer = Customer.get_by_id(customer_id)
        if customer:
            self.show_customer_detail(customer)

    def show_customer_detail(self, customer):
        dialog = CustomerDetailDialog(self, customer)
        dialog.exec()

    def record_payment(self, customer_id, current_debt):
        from PyQt6.QtWidgets import QInputDialog
        amount, ok = QInputDialog.getDouble(
            self, "Record Payment",
            "Payment amount (GHS):",
            value=current_debt,
            min=0.01, max=current_debt,
            decimals=2
        )
        if ok and amount > 0:
            Customer.update_debt(customer_id, -amount)
            self.load_customers()
            self.load_debtors()
            QMessageBox.information(
                self, "Payment Recorded",
                f"Payment of GHS {amount:.2f} recorded.")

    def refresh(self):
        self.load_customers()
        self.load_debtors()


class CustomerDialog(QDialog):

    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(
            "Edit Customer" if customer else "Add Customer")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #e0e0e0; }
            QLineEdit, QTextEdit {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 32px;
            }
            QLineEdit:focus { border: 1px solid #4a9eff; }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
        """)
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name *")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone number")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Notes")

        if self.customer:
            self.name_input.setText(self.customer["name"])
            self.phone_input.setText(self.customer["phone"])
            self.email_input.setText(self.customer.get("email",""))
            self.address_input.setText(
                self.customer.get("address",""))
            self.notes_input.setText(
                self.customer.get("notes",""))

        layout.addRow("Full Name *", self.name_input)
        layout.addRow("Phone", self.phone_input)
        layout.addRow("Email", self.email_input)
        layout.addRow("Address", self.address_input)
        layout.addRow("Notes", self.notes_input)

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
            "Update" if self.customer else "Add Customer")
        save_btn.clicked.connect(self.validate_and_accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addRow("", btn_row)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, "Required", "Please enter customer name.")
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.address_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip()
        }


class CustomerDetailDialog(QDialog):

    def __init__(self, parent, customer):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Customer: " + customer["name"])
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #e0e0e0; }
            QTableWidget {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #0f0f1a;
                color: #6a6a8a;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #2a2a4a;
                font-weight: bold;
            }
        """)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Customer info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        info_layout = QHBoxLayout(info_frame)

        left_info = QVBoxLayout()
        name_lbl = QLabel(self.customer["name"])
        name_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #ffffff;")
        phone_lbl = QLabel("📞 " + (self.customer["phone"] or "N/A"))
        phone_lbl.setStyleSheet("color: #a0a0c0;")
        email_lbl = QLabel(
            "✉️ " + (self.customer.get("email") or "N/A"))
        email_lbl.setStyleSheet("color: #a0a0c0;")
        left_info.addWidget(name_lbl)
        left_info.addWidget(phone_lbl)
        left_info.addWidget(email_lbl)
        info_layout.addLayout(left_info)
        info_layout.addStretch()

        right_info = QVBoxLayout()
        right_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        purchases_lbl = QLabel(
            "Total: GHS {:.2f}".format(
                self.customer["total_purchases"]))
        purchases_lbl.setStyleSheet(
            "color: #00c853; font-size: 16px; font-weight: bold;")
        debt = self.customer["outstanding_debt"]
        debt_lbl = QLabel("Debt: GHS {:.2f}".format(debt))
        debt_lbl.setStyleSheet(
            "color: {}; font-size: 14px; font-weight: bold;".format(
                "#ff1744" if debt > 0 else "#6a6a8a"))
        right_info.addWidget(purchases_lbl)
        right_info.addWidget(debt_lbl)
        info_layout.addLayout(right_info)

        layout.addWidget(info_frame)

        # Purchase history
        history_title = QLabel("Purchase History")
        history_title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #4a9eff;")
        layout.addWidget(history_title)

        history_table = QTableWidget()
        history_table.setColumnCount(5)
        history_table.setHorizontalHeaderLabels([
            "Sale ID", "Items", "Total",
            "Payment", "Date"
        ])
        history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        history_table.verticalHeader().setVisible(False)
        history_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        history_table.setAlternatingRowColors(True)

        history = Customer.get_purchase_history(
            self.customer["id"])
        history_table.setRowCount(len(history))
        for row, h in enumerate(history):
            history_table.setItem(
                row, 0, QTableWidgetItem(str(h["id"])))
            history_table.setItem(
                row, 1, QTableWidgetItem(
                    str(h.get("item_count", 0))))
            history_table.setItem(
                row, 2, QTableWidgetItem(
                    "GHS {:.2f}".format(h["total_amount"])))
            history_table.setItem(
                row, 3, QTableWidgetItem(
                    h["payment_method"].upper()))
            history_table.setItem(
                row, 4, QTableWidgetItem(
                    h["created_at"][:16]))

        layout.addWidget(history_table)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #a0a0c0;
                border-radius: 8px;
                padding: 10px 30px;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(
            close_btn, alignment=Qt.AlignmentFlag.AlignRight)