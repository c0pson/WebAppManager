from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QFrame,
    QToolButton,
    QToolBar,
    QGroupBox,
    QLineEdit
)
from PySide6.QtCore import (
    Qt,
    QSize
)
from PySide6.QtGui import (
    QIcon,
    QPalette
)

from dialogs import AddWebAppDialog, SureRemove
from shortcut import create_shortcut, open_shortcut, remove_shortcut, update_shortcut
from database import Database

class BookmarkWidget(QGroupBox):
    def __init__(self, parent: WebAppManager, app_id: int, icon: QIcon, name: str, url: str, shortcut: str, tag: str | None = None):
        super().__init__(parent)
        self.parent: WebAppManager = parent

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Window)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.icon = icon
        self.app_id = app_id
        self.name = name
        self.url = url
        self.shortcut = shortcut
        self.tag = tag

        self.icon_label = QLabel()
        self.icon_label.setPixmap(AddWebAppDialog.load_icon(icon).pixmap(32, 32))
        self.icon_label.setFixedSize(32, 32)

        self.name_label = QLabel(name)
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)
        self.name_label.setFixedWidth(self.name_label.fontMetrics().averageCharWidth() * 12)
        self.name_label.setToolTip(name)

        self.url_label = QLabel(url)
        self.url_label.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self.url_label,self.setToolTip(url)

        self.tag_label = QLabel(tag or "")
        self.tag_label.setVisible(bool(tag))
        self.tag_label.setContentsMargins(8, 0, 8, 0)

        self.edit_button = QToolButton()
        self.edit_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_button.setToolTip("Edit")
        self.edit_button.clicked.connect(self.on_edit_click)

        self.delete_button = QToolButton()
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_button.setToolTip("Delete")
        self.delete_button.clicked.connect(self.on_delete_click)

        layout = QHBoxLayout(self)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.url_label, 1)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            open_shortcut(self.url, 1080, 720) # TODO: Settings option to change default size of the popup window
        super().mousePressEvent(event)

    def on_delete_click(self):
        dialog = SureRemove(self)
        if dialog.exec():
            self.parent.db.remove(self.app_id)
            self.parent._layout.removeWidget(self)
            remove_shortcut(self.name)
            self.hide()
            self.deleteLater()

    def on_edit_click(self):
        tags = self.parent.db.get_tags()
        dialog = AddWebAppDialog(tags, "Edit Web App", self, self.app_id, tag=self.tag)
        if dialog.exec():
            if data := dialog.get_data():
                icon, name, url, tag = data
            else:
                return
            self.parent.update_app(self.app_id, icon, name, url, tag)
            self.icon_label.setPixmap(AddWebAppDialog.load_icon(icon).pixmap(32, 32))
            self.name_label.setText(name)
            self.url_label.setText(url)
            self.tag_label.setText(tag or "")
            self.tag_label.setVisible(bool(tag))
            new_shortcut = update_shortcut(icon, self.name, name, url)
            self.parent.db.update(self.app_id, shortcut=new_shortcut)
            self.name = name
            self.url = url
            self.tag = tag

class AppMenu(QToolBar):
    def __init__(self, parent: WebAppManager):
        super().__init__(parent)
        self.parent: WebAppManager = parent
        
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setIconSize(QSize(20, 20))

        self.setup()

    def setup(self):
        self.title_label = QLabel("Web App Manager")
        font = self.title_label.font()
        font.setPointSizeF(font.pointSizeF() * 1.35)
        self.title_label.setFont(font)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.addAction(QIcon.fromTheme("search"), QLineEdit.ActionPosition.LeadingPosition)
        self.search_bar.textChanged.connect(self.parent.filter_apps)
        self.search_bar.setMaximumWidth(250)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.add_new_app = QPushButton(text="Add")
        self.add_new_app.setIcon(AddWebAppDialog.load_icon("add"))
        self.add_new_app.clicked.connect(self.on_add_click)

        self.layout().setSpacing(6)
        self.addWidget(self.title_label)
        self.addWidget(spacer)
        self.addWidget(self.search_bar)
        self.addWidget(self.add_new_app)

    def on_add_click(self):
        tags = self.parent.db.get_tags()
        default_icon = "applications-internet"
        dialog = AddWebAppDialog(tags, "Add Web App", self, icon=default_icon)
        if dialog.exec():
            if data := dialog.get_data():
                icon, name, url, tag = data
            else: 
                return
            self.parent.add_app(icon, name, url, tag)

class WebAppManager(QWidget):
    def __init__(self):
        super().__init__()
        self.db: Database = Database()
        self.app_menu = AppMenu(self)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.setup()

    def setup(self):
        self._layout.addWidget(self.app_menu)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.viewport().setBackgroundRole(QPalette.ColorRole.Base)

        self.empty_label = QLabel("Oops, no web apps match your search")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        font = self.empty_label.font()
        font.setPointSizeF(font.pointSizeF() * 1.2)
        self.empty_label.setFont(font)
        self.empty_label.setContentsMargins(0, 40, 0, 0)
        self.empty_label.hide()

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(10)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.container_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.container)
        self._layout.addWidget(self.scroll_area)

        self.create_all_rows()

    def create_all_rows(self):
        for app_id, icon, name, url, shortcut, tag in self.db.get_all():
            widget = BookmarkWidget(self, app_id, icon, name, url, shortcut, tag)
            self.container_layout.addWidget(widget)

    def add_app(self, icon, name, url, tag):
        shortcut = create_shortcut(icon, name, url)
        app_id = self.db.add(icon, name, url, shortcut, tag)
        if app_id is not None:
            widget = BookmarkWidget(self, app_id, icon, name, url, shortcut, tag)
            self.container_layout.addWidget(widget)

    def update_app(self, app_id, icon, name, url, tag):
        self.db.update(app_id, icon=icon, app_name=name, url=url, tag=tag)

    def filter_apps(self, text: str):
        shown = 0
        for i in range(self.container_layout.count()):
            widget = self.container_layout.itemAt(i).widget()
            if isinstance(widget, BookmarkWidget):
                if text.lower() in widget.name.lower() or text in widget.url.lower():
                    widget.show()
                    shown += 1
                else:
                    widget.hide()
        self.empty_label.setVisible(shown == 0)
