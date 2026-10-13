from PySide6.QtWidgets import (
    QApplication,
    QMainWindow
)
from PySide6.QtGui import (
    QFontDatabase,
    QIcon
)
from PySide6.QtCore import Qt

from web_app_manager import WebAppManager

class Application(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_manager = WebAppManager()
        self.setCentralWidget(self.app_manager)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.app_manager.app_menu)

if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationDisplayName("PyWAM")
    app.setWindowIcon(QIcon.fromTheme("webapp-manager"))

    user_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    app.setFont(user_font)

    widget = Application()
    widget.resize(800, 600)
    widget.show()

    app.exec()
