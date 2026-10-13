#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse

BASE_SHORTCUT_DIR = Path.home() / ".local/share/applications"

def create_shortcut(icon: str, name: str, url: str):
    desktop_shortcut_path = BASE_SHORTCUT_DIR / f"pyWAM-{name}.desktop"
    BASE_SHORTCUT_DIR.mkdir(parents=True, exist_ok=True)
    app_path = Path(__file__).resolve()
    content = f"""[Desktop Entry]
Type=Application
Name={name}
Icon={icon}
Exec="{app_path}" --url "{url.replace('%', '%%')}"
Terminal=false
"""
    desktop_shortcut_path.write_text(content)
    desktop_shortcut_path.chmod(0o755)
    subprocess.run(["kbuildsycoca6"], check=False)
    return str(desktop_shortcut_path)

def remove_shortcut(name: str):
    desktop_shortcut_path = BASE_SHORTCUT_DIR / f"pyWAM-{name}.desktop"
    try:
        desktop_shortcut_path.unlink()
    except FileNotFoundError:
        print("No such file?")

def update_shortcut(icon, old_name, name, url):
    remove_shortcut(old_name)
    return create_shortcut(icon, name, url)

def open_shortcut(url: str):
    subprocess.run([
        "chromium-browser",
        f"--app={url}",
        "--start-maximized"
    ], check=True)

def main():
    parser = argparse.ArgumentParser(
        prog="Shortcut Opener for Python Web App Manager",
        description="Opens shortcut for given url in 'app' mode",
    )
    parser.add_argument("-u", "--url", required=True)
    args = parser.parse_args()
    open_shortcut(args.url)

if __name__ == "__main__":
    main()
