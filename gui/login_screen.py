"""
login_screen.py — Login screen using ttkbootstrap widgets.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD,
                    TEXT_SECONDARY, TEXT_MUTED,
                    FONT_FAMILY, FONT_SIZE_LG, FONT_SIZE_MD)


class LoginScreen(tk.Frame):
    """Login card with username/password fields and a Sign In button."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BEIGE)
        self.controller = controller
        self.handler = None

        # Centred card
        card = tk.Frame(self, bg=WHITE, bd=0, relief="flat",
                        highlightbackground="#D0C8BE", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   width=400, height=420)

        # Gold accent
        tk.Frame(card, bg=GOLD, height=4).pack(fill="x")

        # Branding
        tk.Label(card, text="IMBAK",
                 font=(FONT_FAMILY, 24, "bold"),
                 bg=WHITE, fg=OLIVE).pack(pady=(30, 2))
        tk.Label(card, text="Inventory Monitoring and\nBasic Asset Keeper System",
                 font=(FONT_FAMILY, 9),
                 bg=WHITE, fg=TEXT_MUTED, justify="center").pack(pady=(0, 24))

        # Username
        tk.Label(card, text="Username", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY, anchor="w").pack(padx=44, fill="x")
        self.entry_username = ttk.Entry(card, font=(FONT_FAMILY, 11))
        self.entry_username.pack(padx=44, fill="x", ipady=4)

        # Password
        tk.Label(card, text="Password", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY, anchor="w"
                 ).pack(padx=44, fill="x", pady=(14, 0))
        self.entry_password = ttk.Entry(card, font=(FONT_FAMILY, 11), show="\u2022")
        self.entry_password.pack(padx=44, fill="x", ipady=4)

        # Sign In button
        self._btn_login = ttk.Button(
            card, text="Sign In", bootstyle="success",
            command=self._on_login_click,
        )
        self._btn_login.pack(padx=44, fill="x", ipady=6, pady=(28, 0))

        # Enter key shortcut
        self.entry_password.bind("<Return>", lambda e: self._on_login_click())

    def get_credentials(self):
        return (self.entry_username.get().strip(),
                self.entry_password.get().strip())

    def clear_fields(self):
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def _on_login_click(self):
        if self.handler:
            self.handler.handle_login()
