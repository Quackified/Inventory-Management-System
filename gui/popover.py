"""
popover.py — Reusable popover dialog wrapper for Tkinter.

Usage:
    from gui.popover import Popover

    pop = Popover(parent, title="Add Product", width=450, height=350)
    # Add widgets to pop.body
    tk.Label(pop.body, text="Name:").pack()
    pop.add_button("Save", command=on_save)
    pop.add_button("Cancel", command=pop.close, style="secondary")
"""

import tkinter as tk
from config import POPOVER_BG, POPOVER_BORDER, FONT_FAMILY, BTN_PRIMARY


class Popover(tk.Toplevel):
    """
    A modal dialog that centres over the parent window.
    Grabs focus and blocks interaction with the main window.
    """

    def __init__(self, parent, title="Dialog", width=450, height=400):
        super().__init__(parent)

        self.title(title)
        self.configure(bg=POPOVER_BG)
        self.resizable(False, False)
        self.transient(parent)

        # Centre over parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{px}+{py}")

        # Focus grab
        self.grab_set()
        self.focus_set()

        # ── Title bar ────────────────────────────────────────
        title_bar = tk.Frame(self, bg="#ecf0f1")
        title_bar.pack(fill="x")

        tk.Label(title_bar, text=title,
                 font=(FONT_FAMILY, 13, "bold"),
                 bg="#ecf0f1", fg="#2c3e50",
                 padx=16, pady=10).pack(side="left")

        tk.Button(title_bar, text="✕", font=(FONT_FAMILY, 11),
                  bg="#ecf0f1", fg="#e74c3c", relief="flat",
                  activebackground="#fadbd8", cursor="hand2",
                  command=self.close).pack(side="right", padx=8)

        # Separator
        tk.Frame(self, bg=POPOVER_BORDER, height=1).pack(fill="x")

        # ── Body — add your widgets here ─────────────────────
        self.body = tk.Frame(self, bg=POPOVER_BG, padx=20, pady=16)
        self.body.pack(fill="both", expand=True)

        # ── Footer button row ────────────────────────────────
        self._footer = tk.Frame(self, bg="#f7f9fa", padx=16, pady=10)
        self._footer.pack(fill="x", side="bottom")
        tk.Frame(self, bg=POPOVER_BORDER, height=1).pack(fill="x", side="bottom")

        # Fade-in effect
        self.attributes("-alpha", 0.0)
        self._fade_in(0.0)

        # ESC to close
        self.bind("<Escape>", lambda e: self.close())

    def _fade_in(self, alpha):
        """Smooth fade-in animation."""
        if alpha < 1.0:
            alpha = min(alpha + 0.12, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, lambda: self._fade_in(alpha))

    def add_button(self, text, command=None, style="primary"):
        """Add a button to the footer row."""
        if style == "primary":
            bg, fg, active_bg = BTN_PRIMARY, "white", "#3b6baa"
        elif style == "success":
            bg, fg, active_bg = "#27ae60", "white", "#219a52"
        elif style == "danger":
            bg, fg, active_bg = "#d9534f", "white", "#c0392b"
        else:
            bg, fg, active_bg = "#95a5a6", "white", "#7f8c8d"

        btn = tk.Button(
            self._footer, text=text,
            font=(FONT_FAMILY, 10, "bold"), bg=bg, fg=fg,
            activebackground=active_bg, relief="flat",
            cursor="hand2", padx=16, bd=0,
            command=command
        )
        btn.pack(side="left", ipady=4, padx=(0, 8))
        return btn

    def close(self):
        """Close and destroy the popover."""
        self.grab_release()
        self.destroy()

    def add_field(self, label_text, default="", width=30):
        """
        Convenience: add a labelled Entry and return the entry widget.
        """
        row = tk.Frame(self.body, bg=POPOVER_BG)
        row.pack(fill="x", pady=(0, 8))

        tk.Label(row, text=label_text, font=(FONT_FAMILY, 10),
                 bg=POPOVER_BG, fg="#555", width=16, anchor="w").pack(side="left")
        entry = tk.Entry(row, font=(FONT_FAMILY, 10), width=width,
                         relief="solid", bd=1)
        entry.insert(0, default)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def add_dropdown(self, label_text, values, default=""):
        """
        Convenience: add a labelled Combobox and return the widget.
        """
        from tkinter import ttk

        row = tk.Frame(self.body, bg=POPOVER_BG)
        row.pack(fill="x", pady=(0, 8))

        tk.Label(row, text=label_text, font=(FONT_FAMILY, 10),
                 bg=POPOVER_BG, fg="#555", width=16, anchor="w").pack(side="left")
        cmb = ttk.Combobox(row, font=(FONT_FAMILY, 10), width=28,
                           state="readonly", values=values)
        if default:
            cmb.set(default)
        cmb.pack(side="left", fill="x", expand=True)
        return cmb
