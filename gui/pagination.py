"""
pagination.py — Reusable pagination bar using ttkbootstrap.
Matches the reference: "Showing result 1-10 of N Entries" + Previous / Next buttons.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (FONT_FAMILY, WHITE, DARK_BROWN, TEXT_MUTED, BEIGE)


class PaginationBar(tk.Frame):
    """Pagination footer with page info text and Previous/Next buttons."""

    def __init__(self, parent, on_page_change=None, **kwargs):
        kwargs.setdefault("bg", WHITE)
        super().__init__(parent, **kwargs)

        self._page = 1
        self._page_size = 10
        self._total = 0
        self._on_page_change = on_page_change

        # Left: "Showing result 1-10 of N Entries"
        self.lbl_info = tk.Label(
            self, text="Showing result 0 of 0 Entries",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=WHITE,
        )
        self.lbl_info.pack(side="left", padx=(4, 0))

        # Right: page size selector + Previous / Next
        right = tk.Frame(self, bg=WHITE)
        right.pack(side="right")

        # Page size combobox
        self.cmb_size = ttk.Combobox(
            right, values=["10", "25", "50", "100"],
            width=4, state="readonly", font=(FONT_FAMILY, 9),
        )
        self.cmb_size.set("10")
        self.cmb_size.pack(side="left", padx=(0, 12))
        self.cmb_size.bind("<<ComboboxSelected>>", self._on_size_change)

        self.btn_prev = ttk.Button(
            right, text="Previous", bootstyle="secondary-outline",
            command=self._prev,
        )
        self.btn_prev.pack(side="left", padx=(0, 4))

        self.btn_next = ttk.Button(
            right, text="Next", bootstyle="secondary-outline",
            command=self._next,
        )
        self.btn_next.pack(side="left")

    def get_state(self):
        return self._page, self._page_size

    def set_total(self, total):
        self._total = total
        self._update_label()

    def reset(self):
        self._page = 1
        self._update_label()

    def _update_label(self):
        start = (self._page - 1) * self._page_size + 1
        end = min(self._page * self._page_size, self._total)
        if self._total == 0:
            start = 0
            end = 0
        self.lbl_info.config(
            text=f"Showing result {start}-{end} of {self._total} Entries"
        )
        # Enable/disable buttons
        max_page = max(1, (self._total + self._page_size - 1) // self._page_size)
        self.btn_prev.config(state="normal" if self._page > 1 else "disabled")
        self.btn_next.config(state="normal" if self._page < max_page else "disabled")

    def _prev(self):
        if self._page > 1:
            self._page -= 1
            self._fire()

    def _next(self):
        max_page = max(1, (self._total + self._page_size - 1) // self._page_size)
        if self._page < max_page:
            self._page += 1
            self._fire()

    def _on_size_change(self, _event):
        self._page_size = int(self.cmb_size.get())
        self._page = 1
        self._fire()

    def _fire(self):
        self._update_label()
        if self._on_page_change:
            self._on_page_change(self._page, self._page_size)
