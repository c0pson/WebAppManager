#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse
import os

# REFERENCE: chromium-browser --app='https://keep.google.com/#home' -window-size=1080,720
# TODO: Add Icon option to select via system menu
def create_shortcut(name: str, url: str, width: int = 1080, height: int = 720):
    desktop_shortcut_dir = Path.home() / "WebbApps"
    desktop_shortcut_path = desktop_shortcut_dir / f"{name}.desktop"
    desktop_shortcut_dir.mkdir(parents=True, exist_ok=True)
    app_path = Path(__file__).resolve()
    content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec={app_path} --url {url} --width {width} --height {height}
Terminal=false
"""
    desktop_shortcut_path.write_text(content)
    desktop_shortcut_path.chmod(0o755)
    return str(desktop_shortcut_path)

def open_shortcut(url: str, width: int, height: int):
    subprocess.run([
        "chromium-browser",
        f"--app={url}",
        f"--window-size={width},{height}"
    ], check=True)

def main():
    parser = argparse.ArgumentParser(
        prog="Shortcut Opener for Python Web App Manager",
        description="Opens shortcut for given url in 'app' mode",
    )
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    args = parser.parse_args()
    open_shortcut(args.url, args.width, args.height)

if __name__ == "__main__":
    main()
