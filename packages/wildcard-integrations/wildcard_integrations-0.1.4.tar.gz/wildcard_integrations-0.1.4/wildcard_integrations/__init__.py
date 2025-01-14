"""
Wildcard Integrations package providing access to various API clients.
"""

from . import gmail
from . import airtable

__version__ = "0.1.0"
__all__ = ["gmail", "airtable"]
