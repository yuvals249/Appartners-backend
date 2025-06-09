import types
import pytest
import jwt
import datetime
from rest_framework.test import APIClient
from django.conf import settings

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch, settings):
    if getattr(settings, "FIREBASE_MOCK", False):
        stub = types.SimpleNamespace()
        stub.client = lambda: stub              # firestore.client() → stub
        # create / replace firebase_admin.firestore safely
        monkeypatch.setattr("firebase_admin.firestore", stub, raising=False)

@pytest.fixture
def token_header(django_user_model):
    """
    JWT fixture that creates a user + short-lived token
    and returns the ready-to-use Authorization header.
    Uses PyJWT with settings.SECRET_KEY.
    """
    user = django_user_model.objects.create_user(
        username="test_user",
        email="test@example.com",
        password="pass",
    )

    payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    # PyJWT ≥ 2.0 already returns str; if bytes—token.decode()
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
