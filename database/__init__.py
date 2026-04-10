"""
database package — Re-exports connection helpers so existing imports work.

Usage:
    from database import get_connection, close_connection
"""

from database.connection import get_connection, close_connection, DB_CONFIG
