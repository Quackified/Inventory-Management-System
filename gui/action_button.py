"""
action_button.py — Reusable overlay action buttons for Treeview rows.
Places small "..." button widgets over the Actions column cells.
"""

import tkinter as tk
from config import FONT_FAMILY, BORDER_LIGHT

# Button styling — use tk.Button's native activebackground/activeforeground for hover
_BTN_BG        = "#ECECEC"
_BTN_BG_HOVER  = "#D5D5D5"
_BTN_BG_ACTIVE = "#6B7280"
_BTN_FG        = "#555555"
_BTN_FG_ACTIVE = "#FFFFFF"
_BTN_SIZE      = 28


class ActionButtonMixin:
    """Mixin for screens that need action button overlays on a Treeview.

    The host class must have:
        - self.tree : ttk.Treeview
        - self._action_col : str  (e.g. "#11" — the column identifier)
        - self._on_action(item_id, x_root, y_root) : callback
    """

    def _init_action_buttons(self):
        """Call this once after the Treeview + scrollbar are built."""
        self._action_btns = []

        # Reposition overlays on scroll only
        self.tree.bind("<MouseWheel>",
                       lambda e: self._mark_action_dirty())

    def _mark_action_dirty(self):
        """Schedule a single refresh on the next idle cycle."""
        if not getattr(self, '_action_btns_dirty', False):
            self._action_btns_dirty = True
            self.after(30, self._do_refresh_if_dirty)

    def _do_refresh_if_dirty(self):
        if getattr(self, '_action_btns_dirty', False):
            self._action_btns_dirty = False
            self._refresh_action_buttons()

    def _refresh_action_buttons(self):
        """Destroy old buttons and create new ones at current visible rows."""
        for btn in self._action_btns:
            btn.cancel_hover_check()
            btn.destroy()
        self._action_btns.clear()

        for item_id in self.tree.get_children():
            bbox = self.tree.bbox(item_id, column=self._action_col)
            if not bbox:
                continue  # row not visible

            x, y, w, h = bbox
            btn = _ActionLabel(self.tree, item_id, self._on_action)

            # Centre the button in the cell
            bx = x + (w - _BTN_SIZE) // 2
            by = y + (h - _BTN_SIZE) // 2
            btn.place(x=bx, y=by, width=_BTN_SIZE, height=_BTN_SIZE)

            self._action_btns.append(btn)


class _ActionLabel(tk.Button):
    """Small styled button that acts as an action button.
    Uses tk.Button's native activebackground/activeforeground for reliable hover state.
    """

    def __init__(self, parent, item_id, on_action_callback):
        super().__init__(
            parent,
            text="···",
            font=(FONT_FAMILY, 9, "bold"),
            bg=_BTN_BG,
            fg=_BTN_FG,
            activebackground=_BTN_BG_HOVER,  # Native hover highlight
            activeforeground=_BTN_FG,
            cursor="hand2",
            relief="flat",
            bd=0,
            anchor="center",
            command=self._on_click,
        )
        self._item_id = item_id
        self._on_action = on_action_callback

    def _on_click(self):
        """Button click handler."""
        tree = self.master
        tree.selection_set(self._item_id)
        self._on_action(self._item_id, self.winfo_rootx(), self.winfo_rooty())

    def cancel_hover_check(self):
        """No-op for compatibility with existing refresh code."""
        pass

    def destroy(self):
        super().destroy()
