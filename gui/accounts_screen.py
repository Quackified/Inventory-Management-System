"""
accounts_screen.py — Account management using ttkbootstrap.
Same Products-style with ⋯ context menu per row instead of toolbar Edit/Delete.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                    BORDER_LIGHT, ROW_EVEN, ROW_ODD,
                    FONT_FAMILY, ICON_FONT, PAD_SM, PAD_MD, PAD_LG, PAD_XL)
from gui.icons import get_icon
from gui.popover import Popover
from gui.context_menu import ContextMenu
from gui.pagination import PaginationBar
from gui.action_button import ActionButtonMixin


class AccountsScreen(tk.Frame, ActionButtonMixin):
    """Account management — Products-style with action button per row."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))

        tk.Label(header, text="Account Management",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=BG, fg=DARK_BROWN).pack(side="left")

        # ── Toolbar card ─────────────────────────────────────
        toolbar_card = tk.Frame(self, bg=WHITE, bd=0,
                                highlightbackground=BORDER_LIGHT,
                                highlightthickness=1)
        toolbar_card.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        toolbar = tk.Frame(toolbar_card, bg=WHITE, padx=16, pady=10)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text=get_icon("accounts"),
                 font=(ICON_FONT, 14), fg=OLIVE,
                 bg=WHITE).pack(side="left", padx=(0, 8))
        tk.Label(toolbar, text="Users",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        # Only Add is highlighted (consistent with Products)
        ttk.Button(toolbar, text="+ Add User", bootstyle="success",
                   command=self._open_add_popover
                   ).pack(side="right")

        # ── Treeview (with ⋯ column for context menu) ────────
        tree_card = tk.Frame(self, bg=WHITE, bd=0,
                             highlightbackground=BORDER_LIGHT,
                             highlightthickness=1)
        tree_card.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_SM))

        tree_frame = tk.Frame(tree_card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True)

        cols = ("ID", "Username", "Full Name", "Role", "")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=12,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Username": 180, "Full Name": 260,
                      "Role": 110, "": 40}
        for c in cols:
            self.tree.heading(c, text=c if c else "")
            self.tree.column(c, width=col_widths.get(c, 120), anchor="center")

        self.tree.tag_configure("evenrow", background=ROW_EVEN)
        self.tree.tag_configure("oddrow",  background=ROW_ODD)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self._selected_id = None
        self._action_col = "#5"
        self._init_action_buttons()

        # ── Pagination (bottom) ──────────────────────────────
        pager_frame = tk.Frame(self, bg=WHITE, bd=0,
                               highlightbackground=BORDER_LIGHT,
                               highlightthickness=1)
        pager_frame.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))

        self.pager = PaginationBar(pager_frame, bg=WHITE)
        self.pager.pack(fill="x", padx=12, pady=6)

    # ── View interface ───────────────────────────────────────
    def get_selected_id(self):
        return self._selected_id

    def populate_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            alt = "evenrow" if i % 2 == 0 else "oddrow"
            display = (*row, "")
            self.tree.insert("", "end", values=display, tags=(alt,))
        self.pager.set_total(len(rows))
        self.after(50, self._refresh_action_buttons)

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Internal callbacks ───────────────────────────────────
    def _on_tree_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self._selected_id = values[0]

    def _on_action(self, item_id, x_root, y_root):
        """Called by ActionButtonMixin when an action button is clicked."""
        values = self.tree.item(item_id, "values")
        self._selected_id = values[0]
        ContextMenu(
            self.winfo_toplevel(), x_root, y_root,
            on_edit=self._open_edit_popover,
            on_delete=self._on_delete,
        )

    def _get_selected_data(self):
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0], "values")
        return {
            "user_id":   values[0],
            "username":  values[1],
            "full_name": values[2],
            "role":      values[3],
        }

    # ── Popover: Add ─────────────────────────────────────────
    def _open_add_popover(self):
        root = self.winfo_toplevel()
        pop = Popover(root, title="Add User", width=460, height=320)

        e_user = pop.add_field("Username:")
        e_name = pop.add_field("Full Name:")
        e_pass = pop.add_field("Password:")
        cmb_role = pop.add_dropdown("Role:",
                                     values=["Admin", "Manager", "Clerk"],
                                     default="Clerk")

        def on_save():
            if self.handler:
                self.handler.add_from_popover({
                    "username":  e_user.get().strip(),
                    "full_name": e_name.get().strip(),
                    "password":  e_pass.get().strip(),
                    "role":      cmb_role.get(),
                })
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    # ── Popover: Edit ────────────────────────────────────────
    def _open_edit_popover(self):
        data = self._get_selected_data()
        root = self.winfo_toplevel()

        if not data:
            from gui.dialogs import show_warning
            show_warning(root, "Selection",
                         "Select a user from the table first.")
            return

        pop = Popover(root, title=f"Edit User #{data['user_id']}",
                      width=460, height=340)

        e_user = pop.add_field("Username:", default=data["username"])
        e_name = pop.add_field("Full Name:", default=data["full_name"])
        e_pass = pop.add_field("Password:")
        cmb_role = pop.add_dropdown("Role:",
                                     values=["Admin", "Manager", "Clerk"],
                                     default=data["role"])

        tk.Label(pop.body, text="(leave blank to keep current password)",
                 font=(FONT_FAMILY, 9), bg=WHITE, fg=TEXT_MUTED
                 ).pack(anchor="w")

        def on_save():
            if self.handler:
                self.handler.update_from_popover(data["user_id"], {
                    "username":  e_user.get().strip(),
                    "full_name": e_name.get().strip(),
                    "password":  e_pass.get().strip(),
                    "role":      cmb_role.get(),
                })
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    def _on_delete(self):
        if self.handler:
            self.handler.delete()
