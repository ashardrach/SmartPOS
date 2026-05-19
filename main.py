import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SmartPOS Ghana")
    app.setOrganizationName("ashardrach")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()