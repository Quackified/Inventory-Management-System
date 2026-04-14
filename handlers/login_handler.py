"""
login_handler.py — Business logic for user authentication.
"""

from tkinter import messagebox
from models import user_model


class LoginHandler:
    """Handles login form submission: validates input, calls model, updates app."""

    def __init__(self, view, controller):
        self.view = view            # LoginScreen instance
        self.controller = controller  # App instance

    def handle_login(self):
        """Validate credentials and switch to dashboard on success."""
        username, password = self.view.get_credentials()

        # Input validation
        if not username or not password:
            messagebox.showwarning("Input Required",
                                   "Please enter both username and password.")
            return

        # Call model
        user = user_model.authenticate(username, password)

        if user:
            self.controller.current_user = user
            self.controller.on_login_success()
        else:
            messagebox.showerror("Login Failed",
                                 "Invalid username or password.\n")
 
