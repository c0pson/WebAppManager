from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QScrollArea, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from create_dialog import AddWebAppDialog
from shortcut import create_shortcut, open_shortcut
from database import Databse

from style import get_asset

class BookmarkWidget(QWidget):
    def __init__(self, parent: WebAppManager, app_id: int, name: str, url: str, shortcut: str, tag: str | None = None):
        super().__init__(parent, mouseTracking=True)
        self.parent: WebAppManager = parent

        self.setObjectName("bookmark")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.app_id = app_id
        self.url = url
        self.shortcut = shortcut

        self.name_label = QLabel(name)
        self.url_input = QLineEdit(url)
        self.tag_label = QLabel(tag) if tag else None
        
        self.edit_button = QPushButton(text="")
        self.edit_button.setIcon(QIcon(get_asset("edit.svg")))
        self.edit_button.setIconSize(QSize(24, 24))

        self.delete_button = QPushButton(text="")
        self.delete_button.setIcon(QIcon(get_asset("trash.svg")))
        self.delete_button.setIconSize(QSize(24, 24))
        self.delete_button.clicked.connect(self.on_delete_click)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.name_label)
        layout.addWidget(self.url_input)

        if self.tag_label:
            layout.addWidget(self.tag_label)

        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            open_shortcut(self.url, 1080, 720) # TODO: Settings option to change default size of the popup window
        super().mousePressEvent(event)

    def on_delete_click(self):
        self.parent.db.remove(self.app_id)
        self.parent._layout.removeWidget(self)
        self.hide()
        self.deleteLater()

class AppMenu(QWidget):
    def __init__(self, parent: WebAppManager):
        super().__init__(parent)
        self.parent: WebAppManager = parent
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("app_menu")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setup()

    def setup(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.add_new_app = QPushButton(
            text="Add"
        )
        self.add_new_app.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_new_app.clicked.connect(self.on_add_click)
        layout.addWidget(self.add_new_app)
        self.setLayout(layout)

    def on_add_click(self):
        tags = self.parent.db.get_tags()
        dialog = AddWebAppDialog(tags, self)
        if dialog.exec():
            name, url, tag = dialog.get_data()
            self.parent.add_app(name, url, tag)

class WebAppManager(QWidget):
    def __init__(self):
        super().__init__()
        self.db: Databse = Databse()
        self.app_menu = AppMenu(self)
        self.setObjectName("web_app_manager")
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.setup()

    def setup(self):
        self._layout.addWidget(self.app_menu)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 10, 20, 10)
        self.container_layout.setSpacing(10)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container)
        self._layout.addWidget(self.scroll_area)

        self.create_all_rows()

    def create_all_rows(self):
        for app_id, name, url, shortcut, tag in self.db.get_all():
            widget = BookmarkWidget(self, app_id, name, url, shortcut, tag)
            self.container_layout.addWidget(widget)

    def add_app(self, name, url, tag):
        shortcut = create_shortcut(name, url)
        app_id = self.db.add(name, url, shortcut, tag)
        if app_id is not None:
            widget = BookmarkWidget(self, app_id, name, url, shortcut, tag)
            self.container_layout.addWidget(widget)
