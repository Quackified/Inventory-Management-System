"""
login_handler.py — Business logic for user authentication.
"""

from gui.dialogs import show_warning, show_error
from models import user_model


class LoginHandler:
    """Handles login form submission: validates input, calls model, updates app."""

    def __init__(self, view, controller):
        self.view = view            # LoginScreen instance
        self.controller = controller  # App instance

    def handle_login(self):
        """Validate credentials and switch to dashboard on success."""
        username, password = self.view.get_credentials()
        root = self.view.winfo_toplevel()

        # Input validation
        if not username or not password:
            show_warning(root, "Input Required",
                         "Please enter both username and password.")
            return

        # Call model
        user = user_model.authenticate(username, password)

        if user:
            self.controller.current_user = user
            self.controller.on_login_success()
        else:
            show_error(root, "Login Failed",
                       "Invalid username or password.")
