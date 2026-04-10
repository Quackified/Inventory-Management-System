"""
login_screen.py — Login screen UI (no business logic).
"""

import tkinter as tk
from config import BG, CARD_BG, BTN_PRIMARY, FONT_FAMILY


class LoginScreen(tk.Frame):
    """Login card with username/password fields and a Login button."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Login handler reference (set by App after construction) ──
        self.handler = None

        # ── Centred card ─────────────────────────────────────
        card = tk.Frame(self, bg=CARD_BG, bd=0, relief="flat",
                        highlightbackground="#ddd", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=360)

        tk.Label(card, text="Inventory System",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=CARD_BG, fg="#333").pack(pady=(30, 5))
        tk.Label(card, text="Sign in to continue",
                 font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#888").pack(pady=(0, 20))

        # Username
        tk.Label(card, text="Username", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555", anchor="w").pack(padx=40, fill="x")
        self.entry_username = tk.Entry(card, font=(FONT_FAMILY, 11),
                                       relief="solid", bd=1)
        self.entry_username.pack(padx=40, fill="x", ipady=4)

        # Password
        tk.Label(card, text="Password", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555", anchor="w").pack(padx=40, fill="x",
                                                          pady=(12, 0))
        self.entry_password = tk.Entry(card, font=(FONT_FAMILY, 11),
                                       show="\u2022", relief="solid", bd=1)
        self.entry_password.pack(padx=40, fill="x", ipady=4)

        # Login button
        tk.Button(
            card, text="Login", font=(FONT_FAMILY, 11, "bold"),
            bg=BTN_PRIMARY, fg="white", activebackground="#3b6baa",
            activeforeground="white", cursor="hand2",
            relief="flat", bd=0, command=self._on_login_click
        ).pack(padx=40, fill="x", ipady=6, pady=(24, 0))

        # Enter key shortcut
        self.entry_password.bind("<Return>", lambda e: self._on_login_click())

    # ── View interface methods ───────────────────────────────
    def get_credentials(self):
        """Return (username, password) from the form fields."""
        return (self.entry_username.get().strip(),
                self.entry_password.get().strip())

    def clear_fields(self):
        """Clear both input fields."""
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    # ── Internal ─────────────────────────────────────────────
    def _on_login_click(self):
        """Delegate the login action to the handler."""
        if self.handler:
            self.handler.handle_login()
