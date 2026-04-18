"""
accounts_handler.py — Business logic for account management (Admin only).
Now supports popover-based Add/Edit in addition to toolbar Delete.
"""

from gui.dialogs import show_success, show_warning, show_error, show_confirm
from models import user_model


class AccountsHandler:
    """Validates input, calls user model, refreshes the accounts screen."""

    def __init__(self, view, controller):
        self.view = view
        self.controller = controller

    def refresh(self):
        rows = user_model.get_all()
        self.view.populate_table(rows)

    def add_from_popover(self, data):
        """Add a user from popover form data dict."""
        root = self.view.winfo_toplevel()

        if not data["username"]:
            show_warning(root, "Validation", "Username is required.")
            return
        if not data["full_name"]:
            show_warning(root, "Validation", "Full name is required.")
            return
        if not data["password"]:
            show_warning(root, "Validation",
                         "Password is required for new users.")
            return

        success, msg = user_model.add(
            data["username"], data["password"],
            data["full_name"], data["role"]
        )
        if success:
            show_success(root, "User Added", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def update_from_popover(self, user_id, data):
        """Update a user from popover form data dict."""
        root = self.view.winfo_toplevel()

        if not data["username"]:
            show_warning(root, "Validation", "Username is required.")
            return
        if not data["full_name"]:
            show_warning(root, "Validation", "Full name is required.")
            return

        # Prevent admin from changing their own role
        current_user = self.controller.current_user
        if current_user and str(current_user["user_id"]) == str(user_id):
            if data["role"] != current_user["role"]:
                show_warning(root, "Warning",
                             "You cannot change your own role.")
                return

        success, msg = user_model.update(
            user_id, data["username"], data["full_name"],
            data["role"], data["password"] if data["password"] else None
        )
        if success:
            show_success(root, "User Updated", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def delete(self):
        """Delete the selected user after confirmation."""
        root = self.view.winfo_toplevel()
        user_id = self.view.get_selected_id()
        if not user_id:
            show_warning(root, "Selection",
                         "Select a user from the table first.")
            return

        current_user = self.controller.current_user
        if current_user and str(current_user["user_id"]) == str(user_id):
            show_warning(root, "Warning",
                         "You cannot delete your own account.")
            return

        confirm = show_confirm(
            root, "Confirm Delete",
            f"Are you sure you want to delete user #{user_id}?"
        )
        if not confirm:
            return

        success, msg = user_model.delete(user_id)
        if success:
            show_success(root, "User Deleted", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)
