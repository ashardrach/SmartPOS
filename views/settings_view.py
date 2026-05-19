from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("⚙️ Settings — Coming Next")
        label.setStyleSheet("font-size: 24px; color: #4a9eff;")
        layout.addWidget(label)

    def refresh(self): pass