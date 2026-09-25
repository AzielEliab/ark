import os
import subprocess

PALETTE = ["red", "orange", "yellow", "green", "cyan", "blue", "indigo", "violet", "pink", "white", "gray", "black"]
THEME_BG = "#000000"
THEME_PANEL = "#0b0b0b"
THEME_FG = "#d4af37"
FOCUS = "#c9a227"
TAG_HEX = {
    "red": "#f44",
    "orange": "#f93",
    "yellow": "#fe6",
    "green": "#5f8",
    "cyan": "#4df",
    "blue": "#47f",
    "indigo": "#75f",
    "violet": "#b4f",
    "pink": "#f6d",
    "white": "#fff",
    "gray": "#bbb",
    "black": "#000",
}


def normalize_color(s: str) -> str:
    return (s or "").strip().lower()


def tag_to_hex(tag: str) -> str:
    return TAG_HEX.get(normalize_color(tag), "")


def prefers_dark() -> bool:
    """Follow the desktop color scheme when it can be read. Paper otherwise."""
    forced = os.environ.get("ARK_COLOR_SCHEME", "").strip().lower()
    if forced in {"dark", "light"}:
        return forced == "dark"
    gtk = os.environ.get("GTK_THEME", "")
    if "dark" in gtk.lower():
        return True
    try:
        proc = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=1,
            check=False,
        )
        out = (proc.stdout or "").lower()
        if "dark" in out:
            return True
    except (OSError, subprocess.SubprocessError):
        pass
    return False


def system_theme() -> dict[str, str]:
    if prefers_dark():
        return {
            "bg": "#12110e",
            "panel": "#1c1b17",
            "fg": "#f4efe4",
            "muted": "#c8bba6",
            "line": "#3a3428",
            "gold": "#c9a227",
            "on_gold": "#1a1408",
        }
    return {
        "bg": "#f6f3ea",
        "panel": "#fffcf6",
        "fg": "#1c1915",
        "muted": "#4e493f",
        "line": "#e4dcc8",
        "gold": "#c9a227",
        "on_gold": "#1a1408",
    }
