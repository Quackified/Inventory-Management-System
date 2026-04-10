"""
main.py — Inventory Monitoring and Basic Asset Keeper System

OOP Tkinter application with sidebar navigation and modular frames.
Frames: LoginFrame, DashboardFrame, ProductsFrame, TransactionsFrame
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, close_connection
from mysql.connector import Error
from datetime import date


# ═══════════════════════════════════════════════════════════════
#  COLOUR / STYLE CONSTANTS
# ═══════════════════════════════════════════════════════════════
BG           = "#f0f2f5"
SIDEBAR_BG   = "#2c3e50"
SIDEBAR_FG   = "#ecf0f1"
SIDEBAR_ACT  = "#1abc9c"
TOPBAR_BG    = "#4a7abc"
CARD_BG      = "white"
BTN_PRIMARY  = "#4a7abc"
BTN_SUCCESS  = "#27ae60"
BTN_WARNING  = "#e67e22"
BTN_DANGER   = "#d9534f"
FONT_FAMILY  = "Segoe UI"


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION CLASS
# ═══════════════════════════════════════════════════════════════
class App(tk.Tk):
    """Root window — manages login flow and post-login sidebar navigation."""

    def __init__(self):
        super().__init__()

        self.title("Inventory Monitoring and Basic Asset Keeper System")
        self.geometry("1050x620")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.current_user = None    # set after login

        # ── Login frame (shown first, full-screen) ───────────
        self.login_frame = LoginFrame(parent=self, controller=self)
        self.login_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Post-login shell (sidebar + content area) ────────
        self.shell = tk.Frame(self, bg=BG)
        # will be placed after successful login

        self._build_shell()

    # ── Build sidebar + content container ────────────────────
    def _build_shell(self):
        """Create the sidebar and stacked content frames (hidden until login)."""

        # -- Sidebar --
        self.sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App title in sidebar
        tk.Label(self.sidebar, text="IMS",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=SIDEBAR_BG, fg=SIDEBAR_ACT).pack(pady=(24, 4))
        tk.Label(self.sidebar, text="Inventory System",
                 font=(FONT_FAMILY, 9),
                 bg=SIDEBAR_BG, fg="#95a5a6").pack(pady=(0, 20))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard",    "DashboardFrame"),
            ("Products",     "ProductsFrame"),
            ("Transactions", "TransactionsFrame"),
        ]

        for label, frame_name in nav_items:
            btn = tk.Button(
                self.sidebar, text=f"  {label}", anchor="w",
                font=(FONT_FAMILY, 11), bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                activebackground=SIDEBAR_ACT, activeforeground="white",
                relief="flat", cursor="hand2", bd=0, padx=20,
                command=lambda fn=frame_name: self.show_frame(fn)
            )
            btn.pack(fill="x", ipady=10)
            self.nav_buttons[frame_name] = btn

        # Spacer
        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)

        # User info + logout at bottom
        self.lbl_sidebar_user = tk.Label(
            self.sidebar, text="", font=(FONT_FAMILY, 9),
            bg=SIDEBAR_BG, fg="#bdc3c7", wraplength=170, justify="center"
        )
        self.lbl_sidebar_user.pack(pady=(0, 4))

        tk.Button(
            self.sidebar, text="Logout", font=(FONT_FAMILY, 9),
            bg=BTN_DANGER, fg="white", activebackground="#c0392b",
            relief="flat", cursor="hand2",
            command=self.logout
        ).pack(fill="x", padx=20, pady=(0, 20), ipady=4)

        # -- Content area --
        self.content = tk.Frame(self.shell, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Create all content frames
        self.frames = {}
        for FrameClass in (DashboardFrame, ProductsFrame, TransactionsFrame):
            frame = FrameClass(parent=self.content, controller=self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    # ── Navigation ───────────────────────────────────────────
    def show_frame(self, frame_name):
        """Raise a content frame and highlight its sidebar button."""
        # Update sidebar highlight
        for fn, btn in self.nav_buttons.items():
            if fn == frame_name:
                btn.config(bg=SIDEBAR_ACT, fg="white")
            else:
                btn.config(bg=SIDEBAR_BG, fg=SIDEBAR_FG)

        frame = self.frames[frame_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def on_login_success(self):
        """Called by LoginFrame after successful authentication."""
        self.lbl_sidebar_user.config(
            text=f"{self.current_user['username']}  ({self.current_user['role']})"
        )
        self.login_frame.place_forget()
        self.shell.place(x=0, y=0, relwidth=1, relheight=1)
        self.show_frame("DashboardFrame")

    def logout(self):
        """Return to login screen."""
        self.current_user = None
        self.shell.place_forget()
        self.login_frame.entry_username.delete(0, tk.END)
        self.login_frame.entry_password.delete(0, tk.END)
        self.login_frame.place(x=0, y=0, relwidth=1, relheight=1)


# ═══════════════════════════════════════════════════════════════
#  LOGIN FRAME
# ═══════════════════════════════════════════════════════════════
class LoginFrame(tk.Frame):
    """Login card with dummy authentication (admin / password)."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        card = tk.Frame(self, bg=CARD_BG, bd=0, relief="flat",
                        highlightbackground="#ddd", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=360)

        tk.Label(card, text="Inventory System",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=CARD_BG, fg="#333").pack(pady=(30, 5))
        tk.Label(card, text="Sign in to continue",
                 font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#888").pack(pady=(0, 20))

        tk.Label(card, text="Username", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555", anchor="w").pack(padx=40, fill="x")
        self.entry_username = tk.Entry(card, font=(FONT_FAMILY, 11),
                                       relief="solid", bd=1)
        self.entry_username.pack(padx=40, fill="x", ipady=4)

        tk.Label(card, text="Password", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555", anchor="w").pack(padx=40, fill="x",
                                                          pady=(12, 0))
        self.entry_password = tk.Entry(card, font=(FONT_FAMILY, 11),
                                       show="\u2022", relief="solid", bd=1)
        self.entry_password.pack(padx=40, fill="x", ipady=4)

        tk.Button(
            card, text="Login", font=(FONT_FAMILY, 11, "bold"),
            bg=BTN_PRIMARY, fg="white", activebackground="#3b6baa",
            activeforeground="white", cursor="hand2",
            relief="flat", bd=0, command=self.authenticate
        ).pack(padx=40, fill="x", ipady=6, pady=(24, 0))

        self.entry_password.bind("<Return>", lambda e: self.authenticate())

    def authenticate(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required",
                                   "Please enter both username and password.")
            return

        if username == "admin" and password == "password":
            self.controller.current_user = {"username": username, "role": "Admin"}
            self.controller.on_login_success()
        else:
            messagebox.showerror("Login Failed",
                                 "Invalid username or password.\n"
                                 "Hint: admin / password")


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD FRAME
# ═══════════════════════════════════════════════════════════════
class DashboardFrame(tk.Frame):
    """Dashboard with summary cards and recent transactions table."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(header, text="Dashboard",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Summary cards ────────────────────────────────────
        self.cards_frame = tk.Frame(self, bg=BG)
        self.cards_frame.pack(fill="x", padx=24, pady=20)

        self.card_labels = {}
        card_defs = [
            ("total_products",   "Total Products",      "0", BTN_SUCCESS),
            ("low_stock",        "Low Stock (< 10)",     "0", BTN_WARNING),
            ("txn_today",        "Transactions Today",   "0", "#2980b9"),
        ]

        for key, title, val, color in card_defs:
            card = tk.Frame(self.cards_frame, bg=CARD_BG, bd=0,
                            highlightbackground="#ddd", highlightthickness=1)
            card.pack(side="left", padx=10, ipadx=28, ipady=14)

            tk.Label(card, text=title, font=(FONT_FAMILY, 10),
                     bg=CARD_BG, fg="#888").pack()
            lbl = tk.Label(card, text=val, font=(FONT_FAMILY, 28, "bold"),
                           bg=CARD_BG, fg=color)
            lbl.pack()
            self.card_labels[key] = lbl

        # ── Recent transactions table ────────────────────────
        tk.Label(self, text="Recent Transactions",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(10, 6))

        cols = ("ID", "Product", "Type", "Qty", "Date", "User")
        self.tree_recent = ttk.Treeview(self, columns=cols,
                                        show="headings", height=8)
        for c in cols:
            self.tree_recent.heading(c, text=c)
            self.tree_recent.column(c, width=110, anchor="center")
        self.tree_recent.pack(fill="x", padx=24)

    def on_show(self):
        """Pull live stats from the database (graceful fallback)."""
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM products")
            self.card_labels["total_products"].config(text=str(cur.fetchone()[0]))

            cur.execute("SELECT COUNT(*) FROM products WHERE current_stock < 10")
            self.card_labels["low_stock"].config(text=str(cur.fetchone()[0]))

            cur.execute("SELECT COUNT(*) FROM transactions WHERE DATE(transaction_date) = %s",
                        (date.today(),))
            self.card_labels["txn_today"].config(text=str(cur.fetchone()[0]))

            # Recent transactions
            cur.execute("""
                SELECT t.transaction_id, p.name, t.type, t.quantity,
                       DATE_FORMAT(t.transaction_date, '%%Y-%%m-%%d'), t.user_id
                FROM transactions t
                JOIN products p ON t.product_id = p.product_id
                ORDER BY t.transaction_date DESC
                LIMIT 10
            """)
            rows = cur.fetchall()

            for item in self.tree_recent.get_children():
                self.tree_recent.delete(item)
            for row in rows:
                self.tree_recent.insert("", "end", values=row)

            cur.close()
        except Error as e:
            print(f"[Dashboard] Query error: {e}")
        finally:
            close_connection(conn)


# ═══════════════════════════════════════════════════════════════
#  PRODUCTS FRAME  (Full CRUD)
# ═══════════════════════════════════════════════════════════════
class ProductsFrame(tk.Frame):
    """
    Product management screen.
    - Treeview list of all products
    - Entry fields + Add / Update / Delete buttons
    - Connected to real MySQL queries via database.py
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Product Management",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # Search bar (right side of header)
        search_frame = tk.Frame(header, bg=BG)
        search_frame.pack(side="right")

        tk.Label(search_frame, text="Search:",
                 font=(FONT_FAMILY, 10), bg=BG, fg="#555").pack(side="left")
        self.entry_search = tk.Entry(search_frame, font=(FONT_FAMILY, 10),
                                     width=22, relief="solid", bd=1)
        self.entry_search.pack(side="left", padx=(6, 6), ipady=2)
        self.entry_search.bind("<KeyRelease>", lambda e: self._search_products())

        tk.Button(search_frame, text="Clear", font=(FONT_FAMILY, 9),
                  bg="#95a5a6", fg="white", relief="flat", cursor="hand2",
                  command=self._clear_search).pack(side="left", ipady=1)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24)

        cols = ("ID", "Name", "Description", "Stock", "Unit")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=12,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Name": 180, "Description": 260,
                      "Stock": 80, "Unit": 70}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Clicking a row populates the entry fields
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ── Entry fields panel ───────────────────────────────
        form = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#ddd", highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(10, 20))

        # Row 1 — Name, Unit
        r1 = tk.Frame(form, bg=CARD_BG)
        r1.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(r1, text="Name:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_name = tk.Entry(r1, font=(FONT_FAMILY, 10), width=28,
                                   relief="solid", bd=1)
        self.entry_name.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Unit:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_unit = tk.Entry(r1, font=(FONT_FAMILY, 10), width=10,
                                   relief="solid", bd=1)
        self.entry_unit.insert(0, "pcs")
        self.entry_unit.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Stock:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_stock = tk.Entry(r1, font=(FONT_FAMILY, 10), width=8,
                                    relief="solid", bd=1)
        self.entry_stock.pack(side="left", padx=(6, 0))

        # Row 2 — Description
        r2 = tk.Frame(form, bg=CARD_BG)
        r2.pack(fill="x", padx=16, pady=(4, 8))

        tk.Label(r2, text="Description:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_desc = tk.Entry(r2, font=(FONT_FAMILY, 10), width=60,
                                   relief="solid", bd=1)
        self.entry_desc.pack(side="left", padx=(6, 0), fill="x", expand=True)

        # Row 3 — Buttons
        r3 = tk.Frame(form, bg=CARD_BG)
        r3.pack(fill="x", padx=16, pady=(4, 12))

        btn_style = dict(font=(FONT_FAMILY, 10, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=16)

        tk.Button(r3, text="Add Product", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=self._add_product, **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Update Product", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=self._update_product, **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Delete Product", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=self._delete_product, **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Clear Fields", bg="#95a5a6",
                  activebackground="#7f8c8d",
                  command=self._clear_fields, **btn_style
                  ).pack(side="right", ipady=4)

        # Hidden ID tracker (not shown to user)
        self._selected_id = None

    # ── Helpers ──────────────────────────────────────────────
    def _clear_fields(self):
        self._selected_id = None
        for entry in (self.entry_name, self.entry_desc,
                      self.entry_stock, self.entry_unit):
            entry.delete(0, tk.END)
        self.entry_unit.insert(0, "pcs")
        # Deselect treeview row
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def _on_tree_select(self, _event):
        """Populate form fields from the selected Treeview row."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self._selected_id = values[0]

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])

        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[2] if values[2] else "")

        self.entry_stock.delete(0, tk.END)
        self.entry_stock.insert(0, values[3])

        self.entry_unit.delete(0, tk.END)
        self.entry_unit.insert(0, values[4])

    def _validate_inputs(self):
        """Return (name, description, stock, unit) or None on failure."""
        name = self.entry_name.get().strip()
        desc = self.entry_desc.get().strip()
        stock = self.entry_stock.get().strip()
        unit = self.entry_unit.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Product name is required.")
            return None
        if not stock.isdigit():
            messagebox.showwarning("Validation",
                                   "Stock must be a non-negative integer.")
            return None
        return name, desc, int(stock), unit if unit else "pcs"

    # ── CRUD operations ─────────────────────────────────────
    def _add_product(self):
        data = self._validate_inputs()
        if not data:
            return
        name, desc, stock, unit = data

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Could not connect to the database.")
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO products (name, description, current_stock, unit) "
                "VALUES (%s, %s, %s, %s)",
                (name, desc, stock, unit)
            )
            conn.commit()
            cur.close()
            messagebox.showinfo("Success", f"Product '{name}' added.")
            self._clear_fields()
            self._load_products()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            close_connection(conn)

    def _update_product(self):
        if not self._selected_id:
            messagebox.showwarning("Selection",
                                   "Select a product from the table first.")
            return
        data = self._validate_inputs()
        if not data:
            return
        name, desc, stock, unit = data

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Could not connect to the database.")
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE products "
                "SET name=%s, description=%s, current_stock=%s, unit=%s "
                "WHERE product_id=%s",
                (name, desc, stock, unit, self._selected_id)
            )
            conn.commit()
            cur.close()
            messagebox.showinfo("Success", f"Product #{self._selected_id} updated.")
            self._clear_fields()
            self._load_products()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            close_connection(conn)

    def _delete_product(self):
        if not self._selected_id:
            messagebox.showwarning("Selection",
                                   "Select a product from the table first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete product #{self._selected_id}?"
        )
        if not confirm:
            return

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Could not connect to the database.")
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE product_id=%s",
                        (self._selected_id,))
            conn.commit()
            cur.close()
            messagebox.showinfo("Success",
                                f"Product #{self._selected_id} deleted.")
            self._clear_fields()
            self._load_products()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            close_connection(conn)

    # ── Load / refresh ───────────────────────────────────────
    def _load_products(self, search_term=None):
        """Fetch products from the database, optionally filtered by name."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            if search_term:
                cur.execute(
                    "SELECT product_id, name, description, current_stock, unit "
                    "FROM products WHERE name LIKE %s ORDER BY product_id",
                    (f"%{search_term}%",)
                )
            else:
                cur.execute(
                    "SELECT product_id, name, description, current_stock, unit "
                    "FROM products ORDER BY product_id"
                )
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
            cur.close()
        except Error as e:
            print(f"[Products] Load error: {e}")
        finally:
            close_connection(conn)

    def _search_products(self):
        """Filter the Treeview based on the search entry content."""
        term = self.entry_search.get().strip()
        self._load_products(search_term=term if term else None)

    def _clear_search(self):
        """Clear search field and reload all products."""
        self.entry_search.delete(0, tk.END)
        self._load_products()

    def on_show(self):
        self._load_products()


# ═══════════════════════════════════════════════════════════════
#  TRANSACTIONS FRAME  (Stock-In / Stock-Out)
# ═══════════════════════════════════════════════════════════════
class TransactionsFrame(tk.Frame):
    """
    Transaction recording screen.
    - Select a product, choose Stock-In or Stock-Out, enter quantity
    - Records the transaction AND updates product.current_stock
    - Treeview shows full transaction history
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Inventory Transactions",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Input form card ──────────────────────────────────
        form = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#ddd", highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(0, 10))

        # Row 1 — Product selector + Type
        r1 = tk.Frame(form, bg=CARD_BG)
        r1.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(r1, text="Product:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.cmb_product = ttk.Combobox(r1, font=(FONT_FAMILY, 10),
                                         width=30, state="readonly")
        self.cmb_product.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Type:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.txn_type = tk.StringVar(value="Stock-In")
        tk.Radiobutton(r1, text="Stock-In", variable=self.txn_type,
                       value="Stock-In", font=(FONT_FAMILY, 10),
                       bg=CARD_BG, activebackground=CARD_BG,
                       fg="#27ae60", selectcolor=CARD_BG
                       ).pack(side="left", padx=(6, 4))
        tk.Radiobutton(r1, text="Stock-Out", variable=self.txn_type,
                       value="Stock-Out", font=(FONT_FAMILY, 10),
                       bg=CARD_BG, activebackground=CARD_BG,
                       fg="#e74c3c", selectcolor=CARD_BG
                       ).pack(side="left")

        # Row 2 — Quantity + Remarks
        r2 = tk.Frame(form, bg=CARD_BG)
        r2.pack(fill="x", padx=16, pady=(4, 8))

        tk.Label(r2, text="Quantity:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_qty = tk.Entry(r2, font=(FONT_FAMILY, 10), width=8,
                                  relief="solid", bd=1)
        self.entry_qty.pack(side="left", padx=(6, 20))

        tk.Label(r2, text="Remarks:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_remarks = tk.Entry(r2, font=(FONT_FAMILY, 10), width=40,
                                      relief="solid", bd=1)
        self.entry_remarks.pack(side="left", padx=(6, 0), fill="x", expand=True)

        # Row 3 — Record button
        r3 = tk.Frame(form, bg=CARD_BG)
        r3.pack(fill="x", padx=16, pady=(4, 12))

        btn_style = dict(font=(FONT_FAMILY, 10, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=16)

        tk.Button(r3, text="Record Transaction", bg=BTN_PRIMARY,
                  activebackground="#3b6baa",
                  command=self._record_transaction, **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Clear", bg="#95a5a6",
                  activebackground="#7f8c8d",
                  command=self._clear_form, **btn_style
                  ).pack(side="left", ipady=4)

        # ── Transaction history Treeview ──────────────────────
        tk.Label(self, text="Transaction History",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(6, 4))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Product", "Type", "Qty", "Date", "Remarks", "User")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=10,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Product": 160, "Type": 90, "Qty": 60,
                      "Date": 120, "Remarks": 180, "User": 60}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Product map: display_text -> product_id
        self._product_map = {}

    # ── Helpers ──────────────────────────────────────────────
    def _clear_form(self):
        self.cmb_product.set("")
        self.txn_type.set("Stock-In")
        self.entry_qty.delete(0, tk.END)
        self.entry_remarks.delete(0, tk.END)

    def _load_products_combo(self):
        """Refresh the product dropdown from the database."""
        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT product_id, name, current_stock FROM products ORDER BY name"
            )
            rows = cur.fetchall()
            cur.close()

            self._product_map.clear()
            display_list = []
            for pid, name, stock in rows:
                label = f"{name}  (ID:{pid}, Stock:{stock})"
                display_list.append(label)
                self._product_map[label] = pid

            self.cmb_product["values"] = display_list
        except Error as e:
            print(f"[Transactions] Product load error: {e}")
        finally:
            close_connection(conn)

    def _load_transactions(self):
        """Fetch all transactions and populate the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT t.transaction_id, p.name, t.type, t.quantity,
                       DATE_FORMAT(t.transaction_date, '%%Y-%%m-%%d %%H:%%i'),
                       t.remarks, t.user_id
                FROM transactions t
                JOIN products p ON t.product_id = p.product_id
                ORDER BY t.transaction_date DESC
            """)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
            cur.close()
        except Error as e:
            print(f"[Transactions] Load error: {e}")
        finally:
            close_connection(conn)

    # ── Record transaction ───────────────────────────────────
    def _record_transaction(self):
        """INSERT a transaction row and UPDATE the product stock."""
        selected = self.cmb_product.get()
        if not selected or selected not in self._product_map:
            messagebox.showwarning("Validation", "Please select a product.")
            return

        qty_str = self.entry_qty.get().strip()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showwarning("Validation",
                                   "Quantity must be a positive integer.")
            return

        product_id = self._product_map[selected]
        txn_type   = self.txn_type.get()
        quantity   = int(qty_str)
        remarks    = self.entry_remarks.get().strip()
        user_id    = 1  # dummy — linked to the logged-in admin

        # For Stock-Out, check that enough stock exists
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Could not connect to the database.")
            return
        try:
            cur = conn.cursor()

            # Get current stock
            cur.execute("SELECT current_stock FROM products WHERE product_id = %s",
                        (product_id,))
            row = cur.fetchone()
            if row is None:
                messagebox.showerror("Error", "Product not found.")
                return
            current_stock = row[0]

            if txn_type == "Stock-Out" and quantity > current_stock:
                messagebox.showwarning(
                    "Insufficient Stock",
                    f"Only {current_stock} unit(s) available. "
                    f"Cannot stock-out {quantity}."
                )
                return

            # 1) Insert transaction
            cur.execute(
                "INSERT INTO transactions "
                "(product_id, user_id, type, quantity, remarks) "
                "VALUES (%s, %s, %s, %s, %s)",
                (product_id, user_id, txn_type, quantity, remarks)
            )

            # 2) Update product stock
            if txn_type == "Stock-In":
                cur.execute(
                    "UPDATE products SET current_stock = current_stock + %s "
                    "WHERE product_id = %s",
                    (quantity, product_id)
                )
            else:
                cur.execute(
                    "UPDATE products SET current_stock = current_stock - %s "
                    "WHERE product_id = %s",
                    (quantity, product_id)
                )

            conn.commit()
            cur.close()

            messagebox.showinfo(
                "Success",
                f"{txn_type} of {quantity} unit(s) recorded successfully."
            )
            self._clear_form()
            self._load_products_combo()
            self._load_transactions()

        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            close_connection(conn)

    # ── Called every time the frame is shown ─────────────────
    def on_show(self):
        self._load_products_combo()
        self._load_transactions()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
