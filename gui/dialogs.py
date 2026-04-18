"""
dialogs.py — Custom themed modal dialogs using ttkbootstrap.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (FONT_FAMILY, ICON_FONT, WHITE, DARK_BROWN, OLIVE, GOLD,
                    BEIGE, TEXT_MUTED, BORDER_LIGHT,
                    FADE_STEP, FADE_DELAY_MS)


# ── Icon characters (Segoe MDL2 Assets) ─────────────────────
_ICONS = {
    "success": "\uE73E",    # Checkmark
    "warning": "\uE7BA",    # Warning
    "error":   "\uE783",    # Error X
    "confirm": "\uE897",    # Question
}

_COLORS = {
    "success": "#5B8C5A",
    "warning": "#D4A843",
    "error":   "#C0392B",
    "confirm": OLIVE,
}


class _ThemedDialog(tk.Toplevel):
    """Base dialog — thin, clean, centred modal."""

    def __init__(self, parent, title, message, dialog_type="info", buttons=None):
        super().__init__(parent)
        self.result = None

        self.title(title)
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.transient(parent)
        self.overrideredirect(False)

        w, h = 420, 200
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{px}+{py}")

        self.grab_set()
        self.focus_set()

        # Accent bar
        accent_color = _COLORS.get(dialog_type, OLIVE)
        tk.Frame(self, bg=accent_color, height=3).pack(fill="x")

        # Body
        body = tk.Frame(self, bg=WHITE, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # Icon + message row
        row = tk.Frame(body, bg=WHITE)
        row.pack(fill="x", expand=True)

        icon_char = _ICONS.get(dialog_type, "\uE946")
        tk.Label(row, text=icon_char,
                 font=(ICON_FONT, 28), fg=accent_color,
                 bg=WHITE).pack(side="left", padx=(0, 16))

        msg_frame = tk.Frame(row, bg=WHITE)
        msg_frame.pack(side="left", fill="both", expand=True)

        tk.Label(msg_frame, text=title,
                 font=(FONT_FAMILY, 12, "bold"),
                 bg=WHITE, fg=DARK_BROWN, anchor="w").pack(anchor="w")

        tk.Label(msg_frame, text=message,
                 font=(FONT_FAMILY, 10), bg=WHITE, fg=TEXT_MUTED,
                 anchor="w", wraplength=280, justify="left"
                 ).pack(anchor="w", pady=(4, 0))

        # Button row
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x")
        btn_frame = tk.Frame(self, bg=BEIGE, padx=16, pady=10)
        btn_frame.pack(fill="x")

        if buttons is None:
            buttons = [("OK", "success", True)]

        for text, style, retval in reversed(buttons):
            b = ttk.Button(btn_frame, text=text, bootstyle=style,
                           command=lambda rv=retval: self._close(rv))
            b.pack(side="right", padx=(6, 0))

        # Fade in
        self.attributes("-alpha", 0.0)
        self._fade(0.0)

        self.bind("<Escape>", lambda e: self._close(False))
        self.protocol("WM_DELETE_WINDOW", lambda: self._close(False))

    def _fade(self, alpha):
        if alpha < 1.0:
            alpha = min(alpha + FADE_STEP, 1.0)
            self.attributes("-alpha", alpha)
            self.after(FADE_DELAY_MS, lambda: self._fade(alpha))

    def _close(self, result):
        self.result = result
        self.grab_release()
        self.destroy()


# ── Public API ────────────────────────────────────────────────
def show_success(parent, title, message):
    dlg = _ThemedDialog(parent, title, message, "success",
                        buttons=[("OK", "success", True)])
    parent.wait_window(dlg)

def show_warning(parent, title, message):
    dlg = _ThemedDialog(parent, title, message, "warning",
                        buttons=[("OK", "warning", True)])
    parent.wait_window(dlg)

def show_error(parent, title, message):
    dlg = _ThemedDialog(parent, title, message, "error",
                        buttons=[("OK", "danger", True)])
    parent.wait_window(dlg)

def show_confirm(parent, title, message):
    dlg = _ThemedDialog(parent, title, message, "confirm",
                        buttons=[("Yes", "success", True),
                                 ("No", "secondary-outline", False)])
    parent.wait_window(dlg)
    return dlg.result
