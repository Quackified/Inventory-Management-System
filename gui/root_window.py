"""
root_window.py — Root application window using ttkbootstrap.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD, AMBER,
                    SIDEBAR_BG, SIDEBAR_FG, SIDEBAR_ACT, SIDEBAR_HOVER,
                    TEXT_MUTED, TEXT_LIGHT, BORDER_LIGHT,
                    FONT_FAMILY, ICON_FONT, SIDEBAR_WIDTH)

from gui.icons import get_icon
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


# Role access mapping
ROLE_ACCESS = {
    "Admin":   ["DashboardScreen", "ProductsScreen", "TransactionsScreen",
                "WarehouseCategoryScreen", "AccountsScreen"],
    "Manager": ["DashboardScreen", "ProductsScreen", "TransactionsScreen",
                "WarehouseCategoryScreen"],
    "Clerk":   ["DashboardScreen", "ProductsScreen"],
}

SCREEN_LABELS = {
    "DashboardScreen":         "Dashboard",
    "ProductsScreen":          "Products",
    "TransactionsScreen":      "Transactions",
    "WarehouseCategoryScreen": "Warehouses",
    "AccountsScreen":          "Accounts",
}

SCREEN_ICONS = {
    "DashboardScreen":         "dashboard",
    "ProductsScreen":          "products",
    "TransactionsScreen":      "transactions",
    "WarehouseCategoryScreen": "warehouse",
    "AccountsScreen":          "accounts",
}


class App(ttk.Window):
    """Root window — ttkbootstrap themed, sidebar navigation."""

    def __init__(self):
        super().__init__(themename="flatly")

        # Register custom theme BEFORE creating the window
        self._register_imbak_theme()

        self.title("Inventory Monitoring and Basic Asset Keeper System")
        self.geometry("1366x768")
        self.minsize(1100, 650)

        self.current_user = None

        # Apply additional style overrides
        self._setup_custom_styles()

        # Check expired products on startup
        product_model.check_expired()

        # Login screen (shown first)
        self.login_screen = LoginScreen(parent=self, controller=self)
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)
        self.login_screen.handler = LoginHandler(self.login_screen, self)

        # Post-login shell
        self.shell = tk.Frame(self, bg=BG)
        self.sidebar = None
        self.nav_buttons = {}
        self.screens = {}
        self.content = None
        self.lbl_sidebar_user = None

        self._build_shell()

    def _register_imbak_theme(self):
        """Register a custom ttkbootstrap theme using our colour palette."""
        from ttkbootstrap.themes.standard import STANDARD_THEMES
        from ttkbootstrap.style import ThemeDefinition

        theme_def = ThemeDefinition(
            name="imbak",
            themetype="light",
            colors={
                "primary":   "#696B45",   # Olive — main accent
                "secondary": "#A89F95",   # Warm gray
                "success":   "#696B45",   # Olive — highlighted buttons
                "info":      "#C59D50",   # Gold
                "warning":   "#A37C40",   # Amber
                "danger":    "#C0392B",   # Red
                "light":     "#E0D5C9",   # Beige
                "dark":      "#392007",   # Dark brown
                "bg":        "#FFFFFF",   # White background
                "fg":        "#392007",   # Dark brown text
                "selectbg":  "#696B45",   # Olive selection
                "selectfg":  "#FFFFFF",   # White on selection
                "border":    "#D0C8BE",   # Warm border
                "inputfg":   "#392007",   # Input text
                "inputbg":   "#FFFFFF",   # Input background
                "active":    "#556B2F",   # Darker olive for hover/active
            },
        )
        self.style.register_theme(theme_def)
        self.style.theme_use("imbak")

    def _setup_custom_styles(self):
        """Additional style overrides on top of the custom theme."""
        style = self.style

        # Treeview row height and font
        style.configure("Treeview",
                        rowheight=40,
                        font=(f"{FONT_FAMILY} Semibold", 10),
                        borderwidth=0,
                        relief="flat")
        style.configure("Treeview.Heading",
                        font=(FONT_FAMILY, 10, "bold"))

    def _build_shell(self):
        # Sidebar
        self.sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG,
                                width=SIDEBAR_WIDTH)
        self.sidebar.configure(bg=SIDEBAR_BG)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Content area
        self.content = tk.Frame(self.shell, bg=BG)
        self.content.configure(bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Create ALL screens
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

        # Wire handlers
        self.screens["DashboardScreen"].handler = DashboardHandler(
            self.screens["DashboardScreen"])
        self.screens["ProductsScreen"].handler = ProductsHandler(
            self.screens["ProductsScreen"], self)
        self.screens["TransactionsScreen"].handler = TransactionsHandler(
            self.screens["TransactionsScreen"], self)
        self.screens["WarehouseCategoryScreen"].handler = WarehouseCategoryHandler(
            self.screens["WarehouseCategoryScreen"])
        self.screens["AccountsScreen"].handler = AccountsHandler(
            self.screens["AccountsScreen"], self)

    def _render_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.nav_buttons.clear()

        role = self.current_user["role"] if self.current_user else "Clerk"
        allowed = ROLE_ACCESS.get(role, [])

        # Branding
        brand = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        brand.configure(bg=SIDEBAR_BG)
        brand.pack(fill="x", pady=(24, 4))

        lbl_title = tk.Label(brand, text="IMBAK", font=(FONT_FAMILY, 22, "bold"), fg=GOLD)
        lbl_title.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        lbl_title.pack()
        
        lbl_sub = tk.Label(brand, text="Inventory System", font=(FONT_FAMILY, 9), fg=TEXT_LIGHT)
        lbl_sub.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        lbl_sub.pack(pady=(0, 18))

        sep1 = tk.Frame(self.sidebar, bg=SIDEBAR_HOVER, height=1)
        sep1.configure(bg=SIDEBAR_HOVER)
        sep1.pack(fill="x", padx=16, pady=(0, 12))

        # Navigation items
        for screen_name in allowed:
            label     = SCREEN_LABELS.get(screen_name, screen_name)
            icon_name = SCREEN_ICONS.get(screen_name, "info")
            self._create_nav_item(screen_name, label, icon_name)

        # Spacer
        spacer = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        spacer.configure(bg=SIDEBAR_BG)
        spacer.pack(fill="both", expand=True)

        # User info
        sep2 = tk.Frame(self.sidebar, bg=SIDEBAR_HOVER, height=1)
        sep2.configure(bg=SIDEBAR_HOVER)
        sep2.pack(fill="x", padx=16, pady=(0, 8))
        
        self.lbl_sidebar_user = tk.Label(
            self.sidebar, text="", font=(FONT_FAMILY, 9),
            fg=SIDEBAR_FG, wraplength=180, justify="center"
        )
        self.lbl_sidebar_user.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        self.lbl_sidebar_user.pack(pady=(0, 6))

        # Logout
        logout_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG, cursor="hand2")
        logout_frame.configure(bg=SIDEBAR_BG)
        logout_frame.pack(fill="x", padx=16, pady=(0, 20))

        logout_icon = tk.Label(logout_frame, text=get_icon("logout"),
                               font=(ICON_FONT, 11), fg=SIDEBAR_FG)
        logout_icon.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        logout_icon.pack(side="left", padx=(12, 6))

        logout_lbl = tk.Label(logout_frame, text="Sign Out",
                              font=(FONT_FAMILY, 10), fg=SIDEBAR_FG, anchor="w")
        logout_lbl.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        logout_lbl.pack(side="left")

        for w in [logout_frame, logout_icon, logout_lbl]:
            w.bind("<Button-1>", lambda e: self.logout())
            w.bind("<Enter>", lambda e, lf=logout_frame, li=logout_icon, ll=logout_lbl: (
                lf.config(bg=SIDEBAR_HOVER),
                logout_icon.config(bg=SIDEBAR_HOVER),
                logout_lbl.config(bg=SIDEBAR_HOVER)))
            w.bind("<Leave>", lambda e: (
                logout_frame.config(bg=SIDEBAR_BG),
                logout_icon.config(bg=SIDEBAR_BG),
                logout_lbl.config(bg=SIDEBAR_BG)))

    def _create_nav_item(self, screen_name, label, icon_name):
        row = tk.Frame(self.sidebar, bg=SIDEBAR_BG, cursor="hand2")
        row.pack(fill="x")

        indicator = tk.Frame(row, bg=SIDEBAR_BG, width=3)
        indicator.pack(side="left", fill="y")

        icon = tk.Label(row, text=get_icon(icon_name),
                        font=(ICON_FONT, 13), bg=SIDEBAR_BG,
                        fg=GOLD)       # Icons are GOLD for vibrancy
        icon.pack(side="left", padx=(16, 10), pady=12)

        text = tk.Label(row, text=label,
                        font=(FONT_FAMILY, 11), bg=SIDEBAR_BG,
                        fg=SIDEBAR_FG, anchor="w")   # Text bright white
        text.pack(side="left", fill="x", expand=True, pady=12)

        widgets = {"frame": row, "indicator": indicator,
                   "icon": icon, "text": text}
        self.nav_buttons[screen_name] = widgets

        for w in [row, icon, text]:
            w.bind("<Button-1>",
                   lambda e, sn=screen_name: self.show_frame(sn))

        def _enter(e, sn=screen_name, ws=widgets):
            if not ws.get("_active"):
                for w in [ws["frame"], ws["icon"], ws["text"]]:
                    w.config(bg=SIDEBAR_HOVER)
                ws["indicator"].config(bg=SIDEBAR_HOVER)

        def _leave(e, sn=screen_name, ws=widgets):
            if not ws.get("_active"):
                for w in [ws["frame"], ws["icon"], ws["text"]]:
                    w.config(bg=SIDEBAR_BG)
                ws["indicator"].config(bg=SIDEBAR_BG)

        for w in [row, icon, text]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

    def show_frame(self, screen_name):
        for sn, ws in self.nav_buttons.items():
            if sn == screen_name:
                ws["_active"] = True
                for w in [ws["frame"], ws["icon"], ws["text"]]:
                    w.config(bg=SIDEBAR_ACT)
                ws["icon"].config(fg="white")
                ws["text"].config(fg="white")
                ws["indicator"].config(bg=GOLD)
            else:
                ws["_active"] = False
                for w in [ws["frame"], ws["icon"], ws["text"]]:
                    w.config(bg=SIDEBAR_BG)
                ws["icon"].config(fg=GOLD)      # Back to GOLD
                ws["text"].config(fg=SIDEBAR_FG) # Back to bright white
                ws["indicator"].config(bg=SIDEBAR_BG)

        screen = self.screens[screen_name]
        screen.tkraise()
        if hasattr(screen, "on_show"):
            screen.on_show()

    def on_login_success(self):
        self._render_sidebar()
        self.lbl_sidebar_user.config(
            text=f"{self.current_user['username']}  ({self.current_user['role']})"
        )
        self.login_screen.place_forget()
        self.shell.place(x=0, y=0, relwidth=1, relheight=1)

        role = self.current_user["role"]
        allowed = ROLE_ACCESS.get(role, [])
        self.show_frame(allowed[0] if allowed else "ProductsScreen")

    def logout(self):
        self.current_user = None
        self.shell.place_forget()
        self.login_screen.clear_fields()
        self.login_screen.place(x=0, y=0, relwidth=1, relheight=1)
