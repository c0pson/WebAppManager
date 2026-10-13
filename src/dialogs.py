from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFormLayout,
    QDialogButtonBox,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import (
    Qt,
    QSize
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from web_app_manager import BookmarkWidget

import shutil
import subprocess

class SureRemove(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Remove Web App")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout()

        layout.addRow(QLabel("Are you sure you want to remove this item?"))
        layout.addWidget(buttons)

        self.setLayout(layout)

class AddWebAppDialog(QDialog):
    def __init__(self, tags: list[str], title: str, parent: BookmarkWidget | None, app_id=None, **kwargs):
        super().__init__(parent)
        self.parent: BookmarkWidget = parent if parent is not None else None

        self.setWindowTitle(title)

        if app_id is not None:
            self.bookmark_data = self.parent.parent.db.get(app_id)
            _, icon, name, url, shortcut, tag = self.bookmark_data
            self.icon = icon
        else:
            self.bookmark_data = None
            self.icon = kwargs["icon"] if "icon" in kwargs else None

        self.icon_button = QPushButton("")
        self.icon_button.clicked.connect(self.on_icon_click)
        self.icon_button.setIconSize(QSize(64, 64))
        self.icon_button.setFixedSize(80, 80)
        self.icon_button.setToolTip("Choose Icon")

        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.url_input.setMinimumWidth(self.url_input.fontMetrics().averageCharWidth() * 32)
        self.name_input.setMinimumWidth(self.name_input.fontMetrics().averageCharWidth() * 32)

        self.tag_combo = QComboBox()
        self.tag_combo.addItem("None")
        self.tag_combo.addItems(tags)
        self.tag_combo.addItem("New tag...")

        if self.bookmark_data:
            if tag in tags:
                index_of_tag = tags.index(tag)
                self.tag_combo.setCurrentIndex(index_of_tag + 1)
            self.name_input.insert(name)
            self.url_input.insert(url)
            self.icon_button.setIcon(self.load_icon(icon))
        elif self.icon:
            self.icon_button.setIcon(self.load_icon(self.icon))

        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("Enter new tag")
        self.new_tag_input.hide()

        self.tag_combo.currentTextChanged.connect(
            self.on_tag_changed
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form = QFormLayout()
        form.addRow("Name:", self.name_input)
        form.addRow("URL:", self.url_input)
        form.addRow("Tag:", self.tag_combo)
        form.addRow("", self.new_tag_input)

        top = QHBoxLayout()
        top.addWidget(self.icon_button, alignment=Qt.AlignmentFlag.AlignTop)
        top.addLayout(form)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(buttons)

    def on_tag_changed(self, text: str):
        self.new_tag_input.setVisible(text == "New tag...")

    def get_data(self):
        name = self.name_input.text()
        url = self.url_input.text()
        icon = self.icon_button.icon().name()
        if self.tag_combo.currentText() == "New tag...":
            tag = self.new_tag_input.text()
        elif self.tag_combo.currentText() == "None":
            tag = None
        else:
            tag = self.tag_combo.currentText()
        if name and url:
            return icon, name, url, tag
        return False

    @staticmethod
    def load_icon(icon: str | None) -> QIcon:
        if not icon:
            return QIcon.fromTheme("applications-internet")
        return QIcon(icon) if icon.startswith("/") else QIcon.fromTheme(icon)

    def on_icon_click(self) -> str | None:
        if shutil.which("kdialog"):
            result = subprocess.run(
                ["kdialog", "--geticon", "Applications", "--title", "Choose icon"],
                capture_output=True, text=True,
            )
            icon = result.stdout.strip()
        else:
            icon, _ = QFileDialog.getOpenFileName(
                self, "Choose icon", "", "Images (*.png *.svg *.ico *.jpg)"
            )

        if icon:
            self.icon_path = icon
            self.icon_button.setIcon(self.load_icon(icon))
        return icon or None
