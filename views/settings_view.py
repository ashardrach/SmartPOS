from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QFrame, QFormLayout, QMessageBox,
    QDoubleSpinBox, QFileDialog, QTabWidget,
    QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt
from database.db import db

class SettingsView(QWidget):

    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Header
        title = QLabel("⚙️ Settings")
        title.setObjectName("page_title")
        subtitle = QLabel("Configure your business information")
        subtitle.setObjectName("page_subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

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

        # Business tab
        biz_tab = self.build_business_tab()
        tabs.addTab(biz_tab, "🏢 Business Info")

        # Receipt tab
        receipt_tab = self.build_receipt_tab()
        tabs.addTab(receipt_tab, "🧾 Receipt Settings")

        # System tab
        system_tab = self.build_system_tab()
        tabs.addTab(system_tab, "🔧 System")

        layout.addWidget(tabs)

    def build_business_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(widget)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form = QFormLayout(form_frame)
        form.setSpacing(15)
        form.setContentsMargins(20, 20, 20, 20)

        input_style = """
            QLineEdit {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                min-height: 36px;
            }
            QLineEdit:focus { border: 1px solid #4a9eff; }
        """

        settings = db.fetchone(
            "SELECT * FROM settings WHERE id = 1")

        self.biz_name = QLineEdit(
            settings.get("business_name", ""))
        self.biz_name.setStyleSheet(input_style)

        self.biz_address = QLineEdit(
            settings.get("business_address", ""))
        self.biz_address.setStyleSheet(input_style)

        self.biz_phone = QLineEdit(
            settings.get("business_phone", ""))
        self.biz_phone.setStyleSheet(input_style)

        self.biz_email = QLineEdit(
            settings.get("business_email", ""))
        self.biz_email.setStyleSheet(input_style)

        self.currency = QLineEdit(
            settings.get("currency_symbol", "GHS"))
        self.currency.setStyleSheet(input_style)

        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setMaximum(100)
        self.tax_rate.setDecimals(1)
        self.tax_rate.setSuffix(" %")
        self.tax_rate.setValue(
            settings.get("tax_rate", 0))
        self.tax_rate.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 14px;
                min-height: 36px;
            }
        """)

        label_style = "color: #a0a0c0; font-size: 13px;"
        for label_text, widget in [
            ("Business Name", self.biz_name),
            ("Address", self.biz_address),
            ("Phone Number", self.biz_phone),
            ("Email", self.biz_email),
            ("Currency Symbol", self.currency),
            ("Tax Rate", self.tax_rate),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(label_style)
            form.addRow(lbl, widget)

        layout.addWidget(form_frame)

        save_btn = QPushButton("💾 Save Business Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                max-width: 280px;
            }
            QPushButton:hover { background-color: #6ab0ff; }
        """)
        save_btn.clicked.connect(self.save_business_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)
        return container

    def build_receipt_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        settings = db.fetchone(
            "SELECT * FROM settings WHERE id = 1")

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
        """)
        form = QFormLayout(form_frame)
        form.setSpacing(15)
        form.setContentsMargins(20, 20, 20, 20)

        input_style = """
            QLineEdit {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 10px 14px;
                min-height: 36px;
            }
            QLineEdit:focus { border: 1px solid #4a9eff; }
        """

        self.receipt_footer = QLineEdit(
            settings.get("receipt_footer",
                         "Thank you for your business!"))
        self.receipt_footer.setStyleSheet(input_style)

        self.logo_path = QLineEdit(
            settings.get("logo_path", ""))
        self.logo_path.setStyleSheet(input_style)
        self.logo_path.setReadOnly(True)
        self.logo_path.setPlaceholderText(
            "No logo selected")

        logo_btn = QPushButton("Browse")
        logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #a0a0c0;
                border-radius: 6px;
                padding: 8px 16px;
            }
        """)
        logo_btn.clicked.connect(self.browse_logo)

        logo_row = QHBoxLayout()
        logo_row.addWidget(self.logo_path)
        logo_row.addWidget(logo_btn)
        logo_widget = QWidget()
        logo_widget.setLayout(logo_row)

        label_style = "color: #a0a0c0; font-size: 13px;"
        for label_text, widget_item in [
            ("Receipt Footer", self.receipt_footer),
            ("Business Logo", logo_widget),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(label_style)
            form.addRow(lbl, widget_item)

        layout.addWidget(form_frame)

        save_btn = QPushButton("💾 Save Receipt Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                max-width: 280px;
            }
            QPushButton:hover { background-color: #6ab0ff; }
        """)
        save_btn.clicked.connect(self.save_receipt_settings)
        layout.addWidget(save_btn)
        layout.addStretch()
        return widget

    def build_system_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Database info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        title = QLabel("Database Information")
        title.setStyleSheet(
            "color: #4a9eff; font-size: 15px; "
            "font-weight: bold; margin-bottom: 10px;")
        info_layout.addWidget(title)

        products = db.fetchone(
            "SELECT COUNT(*) as count FROM products "
            "WHERE is_active=1")
        customers = db.fetchone(
            "SELECT COUNT(*) as count FROM customers")
        sales = db.fetchone(
            "SELECT COUNT(*) as count FROM sales "
            "WHERE status='completed'")

        for label, value in [
            ("Total Products:",
             str(products["count"])),
            ("Total Customers:",
             str(customers["count"])),
            ("Total Sales:",
             str(sales["count"])),
            ("Database File:", "smartpos.db"),
            ("Version:", "SmartPOS Ghana v1.0.0"),
            ("Developer:", "ashardrach"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #6a6a8a; min-width: 150px;")
            val = QLabel(value)
            val.setStyleSheet(
                "color: #e0e0e0; font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            info_layout.addLayout(row)

        layout.addWidget(info_frame)

        # Backup button
        backup_frame = QFrame()
        backup_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f1a;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        backup_layout = QVBoxLayout(backup_frame)

        backup_title = QLabel("Backup & Restore")
        backup_title.setStyleSheet(
            "color: #4a9eff; font-size: 15px; "
            "font-weight: bold; margin-bottom: 10px;")
        backup_layout.addWidget(backup_title)

        backup_info = QLabel(
            "Create a backup of all your business data.")
        backup_info.setStyleSheet("color: #6a6a8a;")
        backup_layout.addWidget(backup_info)

        btn_row = QHBoxLayout()
        backup_btn = QPushButton("📦 Create Backup")
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        backup_btn.clicked.connect(self.create_backup)

        restore_btn = QPushButton("🔄 Restore Backup")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #a0a0c0;
                border-radius: 8px;
                padding: 10px 20px;
            }
        """)
        restore_btn.clicked.connect(self.restore_backup)

        btn_row.addWidget(backup_btn)
        btn_row.addWidget(restore_btn)
        btn_row.addStretch()
        backup_layout.addLayout(btn_row)

        layout.addWidget(backup_frame)
        layout.addStretch()
        return widget

    def save_business_settings(self):
        try:
            db.execute("""
                UPDATE settings SET
                    business_name = ?,
                    business_address = ?,
                    business_phone = ?,
                    business_email = ?,
                    currency_symbol = ?,
                    tax_rate = ?,
                    updated_at = datetime('now')
                WHERE id = 1
            """, (
                self.biz_name.text().strip(),
                self.biz_address.text().strip(),
                self.biz_phone.text().strip(),
                self.biz_email.text().strip(),
                self.currency.text().strip(),
                self.tax_rate.value()
            ))
            QMessageBox.information(
                self, "Saved",
                "Business settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", "Failed to save: " + str(e))

    def save_receipt_settings(self):
        try:
            db.execute("""
                UPDATE settings SET
                    receipt_footer = ?,
                    logo_path = ?,
                    updated_at = datetime('now')
                WHERE id = 1
            """, (
                self.receipt_footer.text().strip(),
                self.logo_path.text().strip()
            ))
            QMessageBox.information(
                self, "Saved",
                "Receipt settings saved!")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", str(e))

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo",
            "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.logo_path.setText(path)

    def create_backup(self):
        import shutil
        import os
        from datetime import datetime
        try:
            base = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base, "smartpos.db")
            backup_dir = os.path.join(base, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                backup_dir,
                f"smartpos_backup_{timestamp}.db")
            shutil.copy2(db_path, backup_path)
            QMessageBox.information(
                self, "Backup Created",
                f"Backup saved to:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(
                self, "Backup Failed", str(e))

    def restore_backup(self):
        import shutil
        import os
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File",
            "", "Database Files (*.db)")
        if not path:
            return
        reply = QMessageBox.warning(
            self, "Confirm Restore",
            "This will replace ALL current data.\n"
            "Are you sure?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                base = os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)))
                db_path = os.path.join(base, "smartpos.db")
                shutil.copy2(path, db_path)
                QMessageBox.information(
                    self, "Restored",
                    "Backup restored. "
                    "Please restart SmartPOS.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Restore Failed", str(e))

    def refresh(self):
        pass