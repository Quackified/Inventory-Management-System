"""
app_shell.py — Root application window with sidebar navigation.
"""

import tkinter as tk
from config import (BG, SIDEBAR_BG, SIDEBAR_FG, SIDEBAR_ACT,
                    BTN_DANGER, FONT_FAMILY)

from gui.login_screen import LoginScreen
from gui.dashboard_screen import DashboardScreen
from gui.products_screen import ProductsScreen
from gui.transactions_screen import TransactionsScreen

from handlers.login_handler import LoginHandler
from handlers.dashboard_handler import DashboardHandler
from handlers.products_handler import ProductsHandler
from handlers.transactions_handler import TransactionsHandler


class App(tk.Tk):
    """Root window — manages login flow and post-login sidebar navigation."""

    def __init__(self):
        super().__init__()

        self.title("Inventory Monitoring and Basic Asset Keeper System")
        self.geometry("1050x620")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.current_user = None

        # ── Login screen (shown first, full-screen) ──────────
        self.login_screen = LoginScreen(parent=self, controller=self)
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)

        # Wire up login handler
        self.login_screen.handler = LoginHandler(self.login_screen, self)

        # ── Post-login shell (sidebar + content) ─────────────
        self.shell = tk.Frame(self, bg=BG)
        self._build_shell()

    # ── Build sidebar + content container ────────────────────
    def _build_shell(self):
        """Create the sidebar and stacked content screens (hidden until login)."""

        # -- Sidebar --
        sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # App title
        tk.Label(sidebar, text="IMS",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=SIDEBAR_BG, fg=SIDEBAR_ACT).pack(pady=(24, 4))
        tk.Label(sidebar, text="Inventory System",
                 font=(FONT_FAMILY, 9),
                 bg=SIDEBAR_BG, fg="#95a5a6").pack(pady=(0, 20))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard",    "DashboardScreen"),
            ("Products",     "ProductsScreen"),
            ("Transactions", "TransactionsScreen"),
        ]

        for label, screen_name in nav_items:
            btn = tk.Button(
                sidebar, text=f"  {label}", anchor="w",
                font=(FONT_FAMILY, 11), bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                activebackground=SIDEBAR_ACT, activeforeground="white",
                relief="flat", cursor="hand2", bd=0, padx=20,
                command=lambda sn=screen_name: self.show_frame(sn)
            )
            btn.pack(fill="x", ipady=10)
            self.nav_buttons[screen_name] = btn

        # Spacer
        tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)

        # User info + logout at bottom
        self.lbl_sidebar_user = tk.Label(
            sidebar, text="", font=(FONT_FAMILY, 9),
            bg=SIDEBAR_BG, fg="#bdc3c7", wraplength=170, justify="center"
        )
        self.lbl_sidebar_user.pack(pady=(0, 4))

        tk.Button(
            sidebar, text="Logout", font=(FONT_FAMILY, 9),
            bg=BTN_DANGER, fg="white", activebackground="#c0392b",
            relief="flat", cursor="hand2",
            command=self.logout
        ).pack(fill="x", padx=20, pady=(0, 20), ipady=4)

        # -- Content area --
        content = tk.Frame(self.shell, bg=BG)
        content.pack(side="left", fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # Create all content screens
        self.screens = {}
        screen_classes = [
            ("DashboardScreen",    DashboardScreen),
            ("ProductsScreen",     ProductsScreen),
            ("TransactionsScreen", TransactionsScreen),
        ]

        for name, ScreenClass in screen_classes:
            screen = ScreenClass(parent=content, controller=self)
            self.screens[name] = screen
            screen.grid(row=0, column=0, sticky="nsew")

        # Wire up handlers
        self.screens["DashboardScreen"].handler = DashboardHandler(
            self.screens["DashboardScreen"]
        )
        self.screens["ProductsScreen"].handler = ProductsHandler(
            self.screens["ProductsScreen"]
        )
        self.screens["TransactionsScreen"].handler = TransactionsHandler(
            self.screens["TransactionsScreen"], self
        )

    # ── Navigation ───────────────────────────────────────────
    def show_frame(self, screen_name):
        """Raise a content screen and highlight its sidebar button."""
        for sn, btn in self.nav_buttons.items():
            if sn == screen_name:
                btn.config(bg=SIDEBAR_ACT, fg="white")
            else:
                btn.config(bg=SIDEBAR_BG, fg=SIDEBAR_FG)

        screen = self.screens[screen_name]
        screen.tkraise()
        if hasattr(screen, "on_show"):
            screen.on_show()

    def on_login_success(self):
        """Called after successful authentication."""
        self.lbl_sidebar_user.config(
            text=f"{self.current_user['username']}  ({self.current_user['role']})"
        )
        self.login_screen.place_forget()
        self.shell.place(x=0, y=0, relwidth=1, relheight=1)
        self.show_frame("DashboardScreen")

    def logout(self):
        """Return to the login screen."""
        self.current_user = None
        self.shell.place_forget()
        self.login_screen.clear_fields()
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)
