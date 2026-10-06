from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget
from PySide6.QtGui import QFont, QFontDatabase

from web_app_manager import WebAppManager
from style import load_stylesheet

class Application(QMainWindow):
    def __init__(self):
        super().__init__()

        central = QWidget()
        self.setCentralWidget(central)

        self.app_manager = WebAppManager()

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.app_manager)

if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationDisplayName("PyWA Manager")

    user_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    app.setFont(user_font)
    load_stylesheet(app)

    widget = Application()
    widget.resize(800, 600)
    widget.show()

    app.exec()
