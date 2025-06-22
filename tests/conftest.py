import pytest
import jwt
import datetime
from rest_framework.test import APIClient
from django.conf import settings
from unittest.mock import Mock
from django.db.models.query import QuerySet

@pytest.fixture
def api_client():
    """Fixture that returns a DRF API client"""
    return APIClient()

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch, settings):
    """Fixture that mocks Firebase for testing"""
    if getattr(settings, "FIREBASE_MOCK", False):
        class FirebaseStub:
            def __init__(self):
                self._counter = 0
                self.SERVER_TIMESTAMP = datetime.datetime.now()

            def client(self):
                return self

            def collection(self, name):
                return self

            def add(self, data):
                self._counter += 1
                firebase_id = f'test_firebase_id_{self._counter}'
                if not hasattr(self, '_messages'):
                    self._messages = {}
                self._messages[firebase_id] = data
                return (None, type('FirebaseDoc', (), {'id': firebase_id})())

            def document(self, doc_id):
                return self

            def update(self, data):
                return None

            def delete(self):
                return None

            def commit(self):
                return None

            def batch(self):
                return self

            def get(self):
                return type('FirebaseDoc', (), {'to_dict': lambda: {}})()

        stub = FirebaseStub()
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
