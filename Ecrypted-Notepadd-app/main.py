import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.resources import get_app_icon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(get_app_icon())
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 