import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QLabel,
    QStackedWidget, QFrame, QSizePolicy,
    QStatusBar, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartPOS Ghana")
        self.setMinimumSize(1200, 700)
        self.showMaximized()
        self.current_page = "dashboard"
        self.load_stylesheet()
        self.build_ui()
        self.start_clock()

    def load_stylesheet(self):
        style_path = os.path.join(BASE_DIR, "assets", "styles.qss")
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Could not load stylesheet:", e)

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = self.build_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        main_layout.addWidget(self.stack)

        # Load pages
        self.load_pages()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.clock_label = QLabel()
        self.status_bar.addPermanentWidget(self.clock_label)
        self.status_bar.showMessage("SmartPOS Ghana — Ready")

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("💼 SmartPOS")
        logo.setObjectName("logo_label")
        layout.addWidget(logo)

        # Business name
        from database.db import db
        settings = db.fetchone(
            "SELECT business_name FROM settings WHERE id=1"
        )
        biz_name = settings["business_name"] if settings else "My Business"
        self.biz_label = QLabel(biz_name)
        self.biz_label.setObjectName("business_label")
        self.biz_label.setWordWrap(True)
        layout.addWidget(self.biz_label)

        # Divider
        div = QFrame()
        div.setObjectName("divider")
        layout.addWidget(div)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard",  "🏠  Dashboard"),
            ("pos",        "🛒  Point of Sale"),
            ("inventory",  "📦  Inventory"),
            ("customers",  "👥  Customers"),
            ("reports",    "📊  Reports"),
            ("settings",   "⚙️   Settings"),
        ]

        for page_id, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, p=page_id: self.navigate(p)
            )
            self.nav_buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Version
        version = QLabel("v1.0.0 — by ashardrach")
        version.setObjectName("label_muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("padding: 10px; font-size: 10px;")
        layout.addWidget(version)

        return sidebar

    def load_pages(self):
        from views.dashboard_view import DashboardView
        from views.pos_view import POSView
        from views.inventory_view import InventoryView
        from views.customers_view import CustomersView
        from views.reports_view import ReportsView
        from views.settings_view import SettingsView

        self.pages = {
            "dashboard":  DashboardView(),
            "pos":        POSView(),
            "inventory":  InventoryView(),
            "customers":  CustomersView(),
            "reports":    ReportsView(),
            "settings":   SettingsView(),
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.navigate("dashboard")

    def navigate(self, page_id):
        for pid, btn in self.nav_buttons.items():
            btn.setObjectName(
                "nav_button_active" if pid == page_id
                else "nav_button"
            )
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if page_id in self.pages:
            self.stack.setCurrentWidget(self.pages[page_id])
            self.current_page = page_id

            if hasattr(self.pages[page_id], "refresh"):
                self.pages[page_id].refresh()

    def start_clock(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = datetime.now().strftime("%A, %d %B %Y  %H:%M:%S")
        self.clock_label.setText(now)