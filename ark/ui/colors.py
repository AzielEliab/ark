PALETTE = ["red", "orange", "yellow", "green", "cyan", "blue", "indigo", "violet", "pink", "white", "gray", "black"]
THEME_BG = "#000000"
THEME_PANEL = "#0b0b0b"
THEME_FG = "#d4af37"
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
