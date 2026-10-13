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
    QLineEdit,
    QComboBox
)
from PySide6.QtCore import (
    Qt,
    QSize
)
from PySide6.QtGui import (
    QIcon,
    QPalette
)

from threading import Thread

from shortcut import create_shortcut, open_shortcut, remove_shortcut, update_shortcut
from dialogs import AddWebAppDialog, SureRemove
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

        self.tag_label = QFrame()
        self.tag_label.setObjectName("tagChip")

        self.tag_icon = QLabel()
        self.tag_icon.setPixmap(AddWebAppDialog.load_icon("tag").pixmap(16, 16))
        self.tag_icon.setFixedSize(16, 16)

        self.tag_text = QLabel()
        self.tag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chip_layout = QHBoxLayout(self.tag_label)
        chip_layout.setContentsMargins(6, 2, 6, 2)
        chip_layout.setSpacing(4)
        chip_layout.addWidget(self.tag_icon)
        chip_layout.addWidget(self.tag_text, 1)

        pal = self.tag_label.palette()
        accent = pal.color(QPalette.ColorRole.Highlight)
        text = pal.color(QPalette.ColorRole.Text)
        self.tag_label.setStyleSheet(f"""
            #tagChip {{
                background-color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 40);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 120);
                border-radius: 9px;
            }}
            #tagChip QLabel {{
                color: {text.name()};
                background: transparent;
                border: none;
            }}
        """)

        fm = self.tag_text.fontMetrics()
        self.tag_label.setFixedWidth(fm.averageCharWidth() * 8 + 16 + 16 + 2 * 4 + 2 * 6 + 2)
        self.set_tag(tag)

        self.edit_button = QToolButton()
        self.edit_button.setAutoRaise(True)
        self.edit_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_button.setToolTip("Edit")
        self.edit_button.clicked.connect(self.on_edit_click)

        self.delete_button = QToolButton()
        self.delete_button.setAutoRaise(True)
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

    def set_tag(self, tag: str | None):
        self.tag = tag
        fm = self.tag_text.fontMetrics()
        self.tag_text.setText(fm.elidedText(tag or "", Qt.TextElideMode.ElideRight, fm.averageCharWidth() * 8))
        self.tag_label.setToolTip(tag or "")
        self.tag_label.setVisible(bool(tag))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            Thread(target=open_shortcut, args=(self.url,)).start() # TODO: Settings option to change default size of the popup window
        super().mousePressEvent(event)

    def on_delete_click(self):
        dialog = SureRemove(self)
        if dialog.exec():
            self.parent.db.remove(self.app_id)
            self.parent._layout.removeWidget(self)
            remove_shortcut(self.name)
            self.hide()
            self.deleteLater()
            self.parent.app_menu.refresh_tags()
            self.parent.filter_apps()

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
        # self.title_label = QLabel("Web App Manager")
        # font = self.title_label.font()
        # font.setPointSizeF(font.pointSizeF() * 1.35)
        # self.title_label.setFont(font)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.addAction(QIcon.fromTheme("search"), QLineEdit.ActionPosition.LeadingPosition)
        self.search_bar.textChanged.connect(lambda _: self.parent.filter_apps())

        sorting_options = [
            ("view-sort-descending", "Newest"),
            ("view-sort-ascending", "Oldest"),
            ("view-sort-ascending-name", "Name (A-Z)"),
            ("view-sort-descending-name", "Name (Z-A)")
        ]

        self.sort_button = QComboBox(self)
        for icon, text in sorting_options:
            self.sort_button.addItem(QIcon.fromTheme(icon), text)
        self.sort_button.setCurrentIndex(1)
        self.sort_button.currentIndexChanged.connect(self.on_sort_changed)

        self.tag_filter = QComboBox(self)
        self.refresh_tags()
        self.tag_filter.currentIndexChanged.connect(lambda _: self.parent.filter_apps())

        self.add_new_app = QPushButton(text="Add")
        self.add_new_app.setIcon(AddWebAppDialog.load_icon("add"))
        self.add_new_app.clicked.connect(self.on_add_click)

        self.layout().setSpacing(6)
        # self.addWidget(self.title_label)
        self.addWidget(self.search_bar)
        self.addWidget(self.sort_button)
        self.addWidget(self.tag_filter)
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
            self.refresh_tags()

    def on_sort_changed(self, index: int):
        by_id = lambda w: w.app_id
        by_name = lambda w: w.name.lower()
        key, reverse = (
            (by_id, True),
            (by_id, False),
            (by_name, False),
            (by_name, True),
        )[index]
        self.parent.sort_apps(key=key, reverse=reverse)

    def refresh_tags(self):
        current = self.tag_filter.currentData()
        self.tag_filter.blockSignals(True)
        self.tag_filter.clear()
        self.tag_filter.addItem(QIcon.fromTheme("tag"), "All", None)
        for tag in self.parent.db.get_tags():
            self.tag_filter.addItem(QIcon.fromTheme("tag"), tag, tag)
        index = self.tag_filter.findData(current)
        self.tag_filter.setCurrentIndex(max(index, 0))
        self.tag_filter.blockSignals(False)

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
        self.app_menu.refresh_tags()

    def filter_apps(self):
        text = self.app_menu.search_bar.text().lower()
        tag = self.app_menu.tag_filter.currentData()
        shown = 0
        for i in range(self.container_layout.count()):
            widget = self.container_layout.itemAt(i).widget()
            if isinstance(widget, BookmarkWidget):
                matches_text = text in widget.name.lower() or text in widget.url.lower()
                matches_tag = tag is None or widget.tag == tag
                visible = matches_text and matches_tag
                widget.setVisible(visible)
                shown += visible
        self.empty_label.setVisible(shown == 0)

    def sort_apps(self, key=lambda w: w.name.lower(), reverse=False):
        widgets = [
            self.container_layout.itemAt(i).widget()
            for i in range(self.container_layout.count())
            if isinstance(self.container_layout.itemAt(i).widget(), BookmarkWidget)
        ]
        for w in widgets:
            self.container_layout.removeWidget(w)
        for i, w in enumerate(sorted(widgets, key=key, reverse=reverse)):
            self.container_layout.insertWidget(i, w)
