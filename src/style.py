from PySide6.QtWidgets import QApplication

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def load_stylesheet(app: QApplication):
    qss_path = BASE_DIR.parent / "style" / "main.qss"
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Stylesheet file '{qss_path}' not found.")

def get_asset(file_name: str):
    return str(BASE_DIR.parent / "assets" / file_name)
