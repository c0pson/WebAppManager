from PySide6.QtWidgets import QDialog, QLineEdit, QComboBox, QPushButton, QFormLayout, QDialogButtonBox

class AddWebAppDialog(QDialog):
    def __init__(self, tags: list[str], parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Web App")

        self.name_input = QLineEdit()
        self.url_input = QLineEdit()

        self.tag_combo = QComboBox()
        self.tag_combo.addItem("None")
        self.tag_combo.addItems(tags)
        self.tag_combo.addItem("New tag...")

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

        layout = QFormLayout(self)

        layout.addRow("Name:", self.name_input)
        layout.addRow("URL:", self.url_input)
        layout.addRow("Tag:", self.tag_combo)
        layout.addRow("", self.new_tag_input)
        layout.addWidget(buttons)

    def on_tag_changed(self, text: str):
        self.new_tag_input.setVisible(text == "New tag...")

    def get_data(self):
        name = self.name_input.text()
        url = self.url_input.text()
        if self.tag_combo.currentText() == "New tag...":
            tag = self.new_tag_input.text()
        elif self.tag_combo.currentText() == "None":
            tag = None
        else:
            tag = self.tag_combo.currentText()
        return name, url, tag
