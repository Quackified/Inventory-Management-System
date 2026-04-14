"""
root_window.py — Root application window with role-based sidebar navigation.
"""

import tkinter as tk
from config import (BG, SIDEBAR_BG, SIDEBAR_FG, SIDEBAR_ACT,
                    BTN_DANGER, FONT_FAMILY)

from gui.login_screen import LoginScreen
from gui.dashboard_screen import DashboardScreen
from gui.products_screen import ProductsScreen
from gui.transactions_screen import TransactionsScreen
from gui.accounts_screen import AccountsScreen
from gui.warehouse_category_screen import WarehouseCategoryScreen

from handlers.login_handler import LoginHandler
from handlers.dashboard_handler import DashboardHandler
from handlers.products_handler import ProductsHandler
from handlers.transactions_handler import TransactionsHandler
from handlers.accounts_handler import AccountsHandler
from handlers.warehouse_category_handler import WarehouseCategoryHandler

from models import product_model


# ── Role → allowed screens mapping ──────────────────────────
ROLE_ACCESS = {
    "Admin":   ["DashboardScreen", "ProductsScreen", "TransactionsScreen",
                "WarehouseCategoryScreen", "AccountsScreen"],
    "Manager": ["DashboardScreen", "ProductsScreen", "TransactionsScreen",
                "WarehouseCategoryScreen"],
    "Clerk":   ["ProductsScreen", "TransactionsScreen"],
}

# Human-readable labels for sidebar buttons
SCREEN_LABELS = {
    "DashboardScreen":          "Dashboard",
    "ProductsScreen":           "Products",
    "TransactionsScreen":       "Transactions",
    "WarehouseCategoryScreen":  "Warehouses",
    "AccountsScreen":           "Accounts",
}


class App(tk.Tk):
    """Root window — manages login flow and post-login sidebar navigation."""

    def __init__(self):
        super().__init__()

        self.title("Inventory Monitoring and Basic Asset Keeper System")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.attributes('-fullscreen', False)

        self.current_user = None

        # ── Check expired products on startup ────────────────
        product_model.check_expired()

        # ── Login screen (shown first, full-screen) ──────────
        self.login_screen = LoginScreen(parent=self, controller=self)
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)

        # Wire up login handler
        self.login_screen.handler = LoginHandler(self.login_screen, self)

        # ── Post-login shell (sidebar + content) ─────────────
        self.shell = tk.Frame(self, bg=BG)
        self.sidebar = None
        self.nav_buttons = {}
        self.screens = {}
        self.content = None
        self.lbl_sidebar_user = None

        self._build_shell()

    # ── Build sidebar + content container ────────────────────
    def _build_shell(self):
        """Create the sidebar frame, content area, and all screens."""

        # -- Sidebar container (buttons added dynamically on login) --
        self.sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # -- Content area --
        self.content = tk.Frame(self.shell, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Create ALL screens upfront
        screen_classes = {
            "DashboardScreen":         DashboardScreen,
            "ProductsScreen":          ProductsScreen,
            "TransactionsScreen":      TransactionsScreen,
            "WarehouseCategoryScreen": WarehouseCategoryScreen,
            "AccountsScreen":          AccountsScreen,
        }

        for name, ScreenClass in screen_classes.items():
            screen = ScreenClass(parent=self.content, controller=self)
            self.screens[name] = screen
            screen.grid(row=0, column=0, sticky="nsew")

        # Wire up handlers
        self.screens["DashboardScreen"].handler = DashboardHandler(
            self.screens["DashboardScreen"]
        )
        self.screens["ProductsScreen"].handler = ProductsHandler(
            self.screens["ProductsScreen"], self
        )
        self.screens["TransactionsScreen"].handler = TransactionsHandler(
            self.screens["TransactionsScreen"], self
        )
        self.screens["WarehouseCategoryScreen"].handler = WarehouseCategoryHandler(
            self.screens["WarehouseCategoryScreen"]
        )
        self.screens["AccountsScreen"].handler = AccountsHandler(
            self.screens["AccountsScreen"], self
        )

    # ── Rebuild sidebar for current user's role ──────────────
    def _render_sidebar(self):
        """Clear and rebuild sidebar buttons based on the current user's role."""

        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.nav_buttons.clear()

        role = self.current_user["role"] if self.current_user else "Clerk"
        allowed_screens = ROLE_ACCESS.get(role, [])

        # App title
        tk.Label(self.sidebar, text="IMBAK",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=SIDEBAR_BG, fg=SIDEBAR_ACT).pack(pady=(24, 4))
        tk.Label(self.sidebar, text="Inventory System",
                 font=(FONT_FAMILY, 9),
                 bg=SIDEBAR_BG, fg="#95a5a6", wraplength=200).pack(pady=(0, 20))

        # Navigation buttons — only for allowed screens
        for screen_name in allowed_screens:
            label = SCREEN_LABELS.get(screen_name, screen_name)
            btn = tk.Button(
                self.sidebar, text=f"  {label}", anchor="w",
                font=(FONT_FAMILY, 11), bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                activebackground=SIDEBAR_ACT, activeforeground="white",
                relief="flat", cursor="hand2", bd=0, padx=20,
                command=lambda sn=screen_name: self.show_frame(sn)
            )
            btn.pack(fill="x", ipady=10)
            self.nav_buttons[screen_name] = btn

        # Spacer
        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)

        # User info at bottom
        self.lbl_sidebar_user = tk.Label(
            self.sidebar, text="", font=(FONT_FAMILY, 9),
            bg=SIDEBAR_BG, fg="#bdc3c7", wraplength=170, justify="center"
        )
        self.lbl_sidebar_user.pack(pady=(0, 4))

        # Logout button
        tk.Button(
            self.sidebar, text="Logout", font=(FONT_FAMILY, 9),
            bg=BTN_DANGER, fg="white", activebackground="#c0392b",
            relief="flat", cursor="hand2",
            command=self.logout
        ).pack(fill="x", padx=20, pady=(0, 20), ipady=4)

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
        self._render_sidebar()

        self.lbl_sidebar_user.config(
            text=f"{self.current_user['username']}  ({self.current_user['role']})"
        )
        self.login_screen.place_forget()
        self.shell.place(x=0, y=0, relwidth=1, relheight=1)

        # Navigate to the first allowed screen for this role
        role = self.current_user["role"]
        allowed = ROLE_ACCESS.get(role, [])
        first_screen = allowed[0] if allowed else "ProductsScreen"
        self.show_frame(first_screen)

    def logout(self):
        """Return to the login screen."""
        self.current_user = None
        self.shell.place_forget()
        self.login_screen.clear_fields()
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)
