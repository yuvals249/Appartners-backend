"""
tests/settings_test.py
Loads only in pytest.  Disables Firebase, spins up a Postgres TestContainer,
and keeps Redis in-memory, without touching production settings or data.
"""

__test__ = False  # ← tell pytest NOT to treat this file as a test module

import os
from importlib import import_module
from unittest import mock

from testcontainers.postgres import PostgresContainer
import firebase_admin
import cloudinary
from cloudinary import uploader

# ── 1) Pretend Firebase is already initialised ────────────────
firebase_admin._apps = {"dummy": mock.Mock(name="firebase_app")}
firebase_admin.initialize_app = mock.Mock(return_value=firebase_admin._apps["dummy"])
firebase_admin.get_app = lambda: firebase_admin._apps["dummy"]
firebase_admin.delete_app = lambda app=None: None

# ── 1b) Mock Cloudinary ──────────────────────────────────────
mock_cloudinary_response = {
    "public_id": "test_public_id",
    "version": "1234567890",
    "signature": "abcdef123456",
    "width": 800,
    "height": 600,
    "format": "jpg",
    "resource_type": "image",
    "created_at": "2025-01-01T00:00:00Z",
    "bytes": 12345,
    "type": "upload",
    "url": "https://test.com/test.jpg",
    "secure_url": "https://test.com/test.jpg",
    "original_filename": "test_image.jpg"
}

uploader.upload = mock.Mock(return_value=mock_cloudinary_response)
uploader.destroy = mock.Mock(return_value={"result": "ok"})

# Create a proper config mock that behaves like a function
class CloudinaryConfigMock:
    def __init__(self):
        super().__setattr__("_config", {
            "cloud_name": "dummy-cloud",
            "api_key": "dummy-key",
            "api_secret": "dummy-secret",
        })

    def __call__(self, **kwargs):
        self._config.update(kwargs)
        return self

    def __getattr__(self, item):
        return self._config.get(item, None)

    def __setattr__(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        return self._config.get(key, default)

    def keys(self):
        return self._config.keys()

cloudinary.config = CloudinaryConfigMock()

# ── 2) Minimal env vars so the original settings file is happy ─
os.environ.setdefault("SECRET_KEY", "dummy-test-only")
os.environ.setdefault("DEBUG", "True")
# ← add these two lines ↓
os.environ.setdefault(
    "FIREBASE_CONFIG",
    '{"type": "service_account", "project_id": "test", '
    '"private_key": "dummy", "client_email": "test@test.com"}',
)

# ── 2b) Cloudinary dummy vars so settings.py is satisfied ─────
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "dummy-cloud")
os.environ.setdefault("CLOUDINARY_API_KEY", "dummy-key")
os.environ.setdefault("CLOUDINARY_API_SECRET", "dummy-secret")

# ── 3) Import the original settings AFTER stubs/env are ready ─
settings = import_module("appartners.settings")
globals().update(settings.__dict__)     # type: ignore

# ── 4) Isolated Postgres TestContainer ───────────────────────
_pg = PostgresContainer("postgres:15-alpine").start()

from urllib.parse import urlparse

conn = urlparse(_pg.get_connection_url())          # e.g. postgres://user:pass@host:port/db
DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": conn.path.lstrip("/"),                 # strip leading /
    "USER": conn.username,
    "PASSWORD": conn.password,
    "HOST": conn.hostname,
    "PORT": conn.port,
}

# ── 5) In-memory Redis / Channel layers ──────────────────────
REDIS_URL = None
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# ── 6) Test-only flags ───────────────────────────────────────
DEBUG = True
SECRET_KEY = "dummy-test-only"
FIREBASE_MOCK = True
CLOUDINARY_MOCK = True  # Add this flag to indicate Cloudinary is mocked
