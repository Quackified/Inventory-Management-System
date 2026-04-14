"""
accounts_screen.py — Account management screen UI (Admin only).
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, BTN_SUCCESS, BTN_WARNING, BTN_DANGER, FONT_FAMILY


class AccountsScreen(tk.Frame):
    """Account management screen for administering user accounts."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Handler reference (set by App) ───────────────────
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Account Management",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24)

        cols = ("ID", "Username", "Full Name", "Role")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=12,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Username": 160, "Full Name": 220, "Role": 100}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 120), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ── Form fields ──────────────────────────────────────
        form = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#ddd", highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(10, 20))

        # Row 1 — Username, Full Name
        r1 = tk.Frame(form, bg=CARD_BG)
        r1.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(r1, text="Username:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_username = tk.Entry(r1, font=(FONT_FAMILY, 10), width=20,
                                       relief="solid", bd=1)
        self.entry_username.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Full Name:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_fullname = tk.Entry(r1, font=(FONT_FAMILY, 10), width=28,
                                       relief="solid", bd=1)
        self.entry_fullname.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Role:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.cmb_role = ttk.Combobox(r1, font=(FONT_FAMILY, 10), width=12,
                                      state="readonly",
                                      values=["Admin", "Manager", "Clerk"])
        self.cmb_role.set("Clerk")
        self.cmb_role.pack(side="left", padx=(6, 0))

        # Row 2 — Password
        r2 = tk.Frame(form, bg=CARD_BG)
        r2.pack(fill="x", padx=16, pady=(4, 8))

        tk.Label(r2, text="Password:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_password = tk.Entry(r2, font=(FONT_FAMILY, 10), width=28,
                                       relief="solid", bd=1, show="\u2022")
        self.entry_password.pack(side="left", padx=(6, 10))

        tk.Label(r2, text="(leave blank to keep current password)",
                 font=(FONT_FAMILY, 9), bg=CARD_BG, fg="#999").pack(side="left")

        # Row 3 — Buttons
        r3 = tk.Frame(form, bg=CARD_BG)
        r3.pack(fill="x", padx=16, pady=(4, 12))

        btn_style = dict(font=(FONT_FAMILY, 10, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=16)

        tk.Button(r3, text="Add User", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=lambda: self._delegate("add"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Update User", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=lambda: self._delegate("update"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Delete User", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=lambda: self._delegate("delete"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Clear Fields", bg="#95a5a6",
                  activebackground="#7f8c8d",
                  command=self.clear_fields, **btn_style
                  ).pack(side="right", ipady=4)

        # Track selected user ID
        self._selected_id = None

    # ── View interface methods ───────────────────────────────
    def get_form_data(self):
        """Return dict with current form field values."""
        return {
            "username": self.entry_username.get().strip(),
            "full_name": self.entry_fullname.get().strip(),
            "password": self.entry_password.get().strip(),
            "role": self.cmb_role.get(),
        }

    def get_selected_id(self):
        """Return the currently selected user ID."""
        return self._selected_id

    def populate_table(self, rows):
        """Clear and repopulate the user Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def clear_fields(self):
        """Clear all form fields and deselect the Treeview row."""
        self._selected_id = None
        self.entry_username.delete(0, tk.END)
        self.entry_fullname.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.cmb_role.set("Clerk")
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def on_show(self):
        """Called when this screen becomes visible."""
        if self.handler:
            self.handler.refresh()

    # ── Internal callbacks ───────────────────────────────────
    def _on_tree_select(self, _event):
        """Populate form from selected Treeview row."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self._selected_id = values[0]

        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, values[1])

        self.entry_fullname.delete(0, tk.END)
        self.entry_fullname.insert(0, values[2])

        self.cmb_role.set(values[3])

        # Clear password field (don't pre-fill)
        self.entry_password.delete(0, tk.END)

    def _delegate(self, action):
        """Forward button click to handler."""
        if self.handler:
            getattr(self.handler, action)()
