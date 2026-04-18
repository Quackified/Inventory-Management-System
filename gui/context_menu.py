"""
context_menu.py — Per-row context menu popup (⋯ button).
Clean plain-text dropdown, click-outside to dismiss.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (FONT_FAMILY, WHITE, DARK_BROWN, BEIGE, TEXT_MUTED,
                    BORDER_LIGHT)


class ContextMenu(tk.Toplevel):
    """Dropdown-style menu shown at (x, y) with Edit / Delete actions."""

    def __init__(self, parent, x, y, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=WHITE, highlightbackground=BORDER_LIGHT,
                       highlightthickness=1)
        self.attributes("-topmost", True)

        # Position next to click
        self.geometry(f"130x72+{x}+{y}")

        # Edit
        edit_frame = tk.Frame(self, bg=WHITE, cursor="hand2")
        edit_frame.pack(fill="x", padx=1, pady=(4, 0))
        edit_lbl = tk.Label(edit_frame, text="Edit", font=(FONT_FAMILY, 10),
                            bg=WHITE, fg=DARK_BROWN, anchor="w", padx=14, pady=6)
        edit_lbl.pack(fill="x")
        for w in [edit_frame, edit_lbl]:
            w.bind("<Button-1>", lambda e: self._action(on_edit))
            w.bind("<Enter>", lambda e: (edit_frame.config(bg=BEIGE),
                                          edit_lbl.config(bg=BEIGE)))
            w.bind("<Leave>", lambda e: (edit_frame.config(bg=WHITE),
                                          edit_lbl.config(bg=WHITE)))

        # Separator
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x", padx=8)

        # Delete
        del_frame = tk.Frame(self, bg=WHITE, cursor="hand2")
        del_frame.pack(fill="x", padx=1, pady=(0, 4))
        del_lbl = tk.Label(del_frame, text="Delete", font=(FONT_FAMILY, 10),
                           bg=WHITE, fg="#C0392B", anchor="w", padx=14, pady=6)
        del_lbl.pack(fill="x")
        for w in [del_frame, del_lbl]:
            w.bind("<Button-1>", lambda e: self._action(on_delete))
            w.bind("<Enter>", lambda e: (del_frame.config(bg="#FFF0F0"),
                                          del_lbl.config(bg="#FFF0F0")))
            w.bind("<Leave>", lambda e: (del_frame.config(bg=WHITE),
                                          del_lbl.config(bg=WHITE)))

        # Click outside to close (bind to root)
        self._root = parent
        self._root.bind("<Button-1>", self._on_root_click, add="+")
        self.bind("<Escape>", lambda e: self._dismiss())

        # Auto-focus
        self.focus_set()

    def _action(self, callback):
        self._unbind_root()
        self.destroy()
        if callback:
            callback()

    def _on_root_click(self, event):
        """Dismiss if click is outside this menu."""
        try:
            wx = self.winfo_rootx()
            wy = self.winfo_rooty()
            ww = self.winfo_width()
            wh = self.winfo_height()
            if not (wx <= event.x_root <= wx + ww and
                    wy <= event.y_root <= wy + wh):
                self._dismiss()
        except tk.TclError:
            pass

    def _dismiss(self):
        self._unbind_root()
        self.destroy()

    def _unbind_root(self):
        try:
            self._root.unbind("<Button-1>")
        except tk.TclError:
            pass
