"""
main.py — Entry point for the Inventory Management System.

Architecture: MVP (Model-View-Presenter)
    models/     — Database operations (SQL queries)
    gui/        — Tkinter screens (UI widgets)
    handlers/   — Business logic (connects GUI to Models)
"""

from gui.app_shell import App


if __name__ == "__main__":
    app = App()
    app.mainloop()
