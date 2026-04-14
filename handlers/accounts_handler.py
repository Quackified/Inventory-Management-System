"""
accounts_handler.py — Business logic for account management (Admin only).
"""

from tkinter import messagebox
from models import user_model


class AccountsHandler:
    """Validates form input, calls user model, refreshes the accounts screen."""

    def __init__(self, view, controller):
        self.view = view              # AccountsScreen instance
        self.controller = controller  # App instance

    def refresh(self):
        """Reload all users into the Treeview."""
        rows = user_model.get_all()
        self.view.populate_table(rows)

    def add(self):
        """Validate and add a new user."""
        data = self._validate()
        if not data:
            return

        if not data["password"]:
            messagebox.showwarning("Validation",
                                   "Password is required for new users.")
            return

        success, msg = user_model.add(
            data["username"], data["password"],
            data["full_name"], data["role"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def update(self):
        """Validate and update the selected user."""
        user_id = self.view.get_selected_id()
        if not user_id:
            messagebox.showwarning("Selection",
                                   "Select a user from the table first.")
            return

        data = self._validate()
        if not data:
            return

        # Prevent admin from changing their own role
        current_user = self.controller.current_user
        if current_user and str(current_user["user_id"]) == str(user_id):
            if data["role"] != current_user["role"]:
                messagebox.showwarning("Warning",
                                       "You cannot change your own role.")
                return

        success, msg = user_model.update(
            user_id, data["username"], data["full_name"],
            data["role"], data["password"] if data["password"] else None
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def delete(self):
        """Delete the selected user after confirmation."""
        user_id = self.view.get_selected_id()
        if not user_id:
            messagebox.showwarning("Selection",
                                   "Select a user from the table first.")
            return

        # Prevent admin from deleting themselves
        current_user = self.controller.current_user
        if current_user and str(current_user["user_id"]) == str(user_id):
            messagebox.showwarning("Warning",
                                   "You cannot delete your own account.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user #{user_id}?"
        )
        if not confirm:
            return

        success, msg = user_model.delete(user_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    # ── Input validation ─────────────────────────────────────
    def _validate(self):
        """
        Validate form data.

        Returns:
            dict or None on failure.
        """
        data = self.view.get_form_data()

        if not data["username"]:
            messagebox.showwarning("Validation", "Username is required.")
            return None

        if not data["full_name"]:
            messagebox.showwarning("Validation", "Full name is required.")
            return None

        if not data["role"]:
            messagebox.showwarning("Validation", "Please select a role.")
            return None

        return data
