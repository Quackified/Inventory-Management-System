"""
popover.py — Reusable modal popover dialog using ttkbootstrap widgets.
No redundant X close button — Cancel button is sufficient.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (FONT_FAMILY, ICON_FONT, DARK_BROWN, OLIVE, WHITE, GOLD,
                    BEIGE, TEXT_SECONDARY, TEXT_MUTED, BORDER_LIGHT,
                    FADE_STEP, FADE_DELAY_MS)


class Popover(tk.Toplevel):
    """Themed modal dialog centred over the parent window."""

    def __init__(self, parent, title="Dialog", width=480, height=420):
        super().__init__(parent)

        self.title(title)
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.transient(parent)

        # Centre over parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{px}+{py}")

        self.grab_set()
        self.focus_set()

        # Gold accent bar
        tk.Frame(self, bg=GOLD, height=3).pack(fill="x")

        # Title bar (NO X button — Cancel is sufficient)
        title_bar = tk.Frame(self, bg=BEIGE)
        title_bar.pack(fill="x")

        tk.Label(title_bar, text=title,
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BEIGE, fg=DARK_BROWN,
                 padx=18, pady=10).pack(side="left")

        # Separator
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x")

        # Body
        self.body = tk.Frame(self, bg=WHITE, padx=22, pady=16)
        self.body.pack(fill="both", expand=True)

        # Footer
        self._footer = tk.Frame(self, bg=BEIGE, padx=18, pady=10)
        self._footer.pack(fill="x", side="bottom")
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x", side="bottom")

        # Fade in
        self.attributes("-alpha", 0.0)
        self._fade_in(0.0)

        self.bind("<Escape>", lambda e: self.close())
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _fade_in(self, alpha):
        if alpha < 1.0:
            alpha = min(alpha + FADE_STEP, 1.0)
            self.attributes("-alpha", alpha)
            self.after(FADE_DELAY_MS, lambda: self._fade_in(alpha))

    def add_button(self, text, command=None, style="success"):
        """Add a ttkbootstrap-styled button to the footer."""
        btn = ttk.Button(self._footer, text=text, bootstyle=style,
                         command=command)
        btn.pack(side="left", padx=(0, 8))
        return btn

    def close(self):
        self.grab_release()
        self.destroy()

    def add_field(self, label_text, default="", width=30):
        """Add a labelled ttk.Entry field."""
        row = tk.Frame(self.body, bg=WHITE)
        row.pack(fill="x", pady=(0, 8))

        tk.Label(row, text=label_text, font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY, width=16, anchor="w"
                 ).pack(side="left")

        entry = ttk.Entry(row, font=(FONT_FAMILY, 10), width=width)
        entry.insert(0, default)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def add_dropdown(self, label_text, values, default=""):
        """Add a labelled ttk.Combobox."""
        row = tk.Frame(self.body, bg=WHITE)
        row.pack(fill="x", pady=(0, 8))

        tk.Label(row, text=label_text, font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY, width=16, anchor="w"
                 ).pack(side="left")

        cmb = ttk.Combobox(row, font=(FONT_FAMILY, 10), width=28,
                           state="readonly", values=values)
        if default:
            cmb.set(default)
        cmb.pack(side="left", fill="x", expand=True)
        return cmb
