"""
Pytest configuration for Nafld Mash Fibrosis Agent test suite.
Sets required environment variables before test collection.
"""
import os

# Set required environment variable before any agent imports
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-for-pytest-2026")
