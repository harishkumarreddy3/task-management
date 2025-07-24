"""
Core Configuration and Dependencies

This module contains application configuration, settings, and dependency injection.
"""

from .config import settings
from .deps import get_db, get_current_user, user_dependency, db_dependency, bcrypt_contex

__all__ = ["settings", "get_db", "get_current_user", "user_dependency", "db_dependency", "bcrypt_contex"]