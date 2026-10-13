#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse

BASE_SHORTCUT_DIR = Path.home() / "WebbApps"

def create_shortcut(icon: str, name: str, url: str, width: int = 1080, height: int = 720): # TODO: Add Icon option to select via system menu
    desktop_shortcut_path = BASE_SHORTCUT_DIR / f"{name}.desktop"
    BASE_SHORTCUT_DIR.mkdir(parents=True, exist_ok=True)
    app_path = Path(__file__).resolve()
    content = f"""[Desktop Entry]
Type=Application
Name={name}
Icon={icon}
Exec={app_path} --url {url} --width {width} --height {height}
Terminal=false
"""
    desktop_shortcut_path.write_text(content)
    desktop_shortcut_path.chmod(0o755)
    return str(desktop_shortcut_path)

def remove_shortcut(name: str):
    desktop_shortcut_path = BASE_SHORTCUT_DIR / f"{name}.desktop"
    try:
        desktop_shortcut_path.unlink()
    except FileNotFoundError:
        print("No such file?")

def update_shortcut(icon, old_name, name, url, width=1080, height=720):
    remove_shortcut(old_name)
    return create_shortcut(icon, name, url, width, height)

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
