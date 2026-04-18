"""
icons.py — Material Design-style icons via Windows Segoe MDL2 Assets font.

Usage:
    from gui.icons import get_icon, icon_label
    lbl = icon_label(parent, "search", size=14, color="#392007")
"""

import tkinter as tk
from config import ICON_FONT

# ── Icon glyph map (Segoe MDL2 Assets codepoints) ───────────
ICON_MAP = {
    # Navigation
    "dashboard":     "\uE80F",   # Home
    "products":      "\uE719",   # Tag
    "transactions":  "\uE8CB",   # SwitchApps
    "warehouse":     "\uE825",   # Map
    "accounts":      "\uE716",   # People
    "logout":        "\uE7E8",   # PowerButton

    # Actions
    "search":        "\uE721",
    "add":           "\uE710",   # Add (+)
    "edit":          "\uE70F",   # Edit (pencil)
    "delete":        "\uE74D",   # Delete (trash)
    "refresh":       "\uE72C",
    "export":        "\uE78C",   # Share
    "filter":        "\uE71C",

    # Navigation arrows
    "chevron_left":  "\uE76B",
    "chevron_right": "\uE76C",
    "chevron_down":  "\uE70D",
    "up":            "\uE74A",
    "down":          "\uE74B",

    # Status / feedback
    "check":         "\uE73E",   # Accept (checkmark)
    "warning":       "\uE7BA",   # Warning (triangle)
    "error":         "\uE783",   # StatusError
    "info":          "\uE946",
    "close":         "\uE711",   # Cancel (X)

    # Misc
    "more":          "\uE712",   # More (three dots)
    "calendar":      "\uE787",
    "stock_in":      "\uE74A",   # UpArrow
    "stock_out":     "\uE74B",   # DownArrow
    "person":        "\uE77B",   # Contact
    "sort":          "\uE8CB",
}


def get_icon(name):
    """Return the unicode character for the named icon."""
    return ICON_MAP.get(name, "\uE946")


def icon_label(parent, name, size=14, color="#392007", bg=None, **kw):
    """Create a tk.Label displaying a Segoe MDL2 Assets icon glyph."""
    char = get_icon(name)
    opts = {"text": char, "font": (ICON_FONT, size), "fg": color}
    if bg is not None:
        opts["bg"] = bg
    opts.update(kw)
    return tk.Label(parent, **opts)
