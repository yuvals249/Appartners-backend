import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from chat.authentication import JWTAuthentication
from appartners.utils import generate_jwt

@pytest.fixture
def request_factory():
    """Fixture ליצירת RequestFactory"""
    return RequestFactory()

@pytest.fixture
def test_user(db):
    """Fixture ליצירת משתמש לבדיקות"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def test_token(test_user):
    """Fixture ליצירת טוקן JWT לבדיקות"""
    return generate_jwt(test_user, 'access')

def test_jwt_authentication_no_token(request_factory):
    """בדיקת אימות ללא טוקן"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    
    auth = JWTAuthentication()
    result = auth.authenticate(request)
    
    assert result is None

def test_jwt_authentication_invalid_token(request_factory):
    """בדיקת אימות עם טוקן לא תקין"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid-token'
    
    auth = JWTAuthentication()
    with pytest.raises(Exception):
        auth.authenticate(request)

def test_jwt_authentication_valid_token(request_factory, test_user, test_token):
    """בדיקת אימות עם טוקן תקין"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {test_token}'
    
    auth = JWTAuthentication()
    result = auth.authenticate(request)
    
    assert result is not None
    assert result[0] == test_user
    assert result[1] is None

def test_jwt_authentication_invalid_header_format(request_factory):
    """בדיקת אימות עם פורמט header לא תקין"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = 'InvalidFormat test-token'
    
    auth = JWTAuthentication()
    result = auth.authenticate(request)
    
    assert result is None

def test_jwt_authentication_refresh_token(request_factory, test_user):
    """בדיקת אימות עם טוקן רענון"""
    refresh_token = generate_jwt(test_user, 'refresh')
    
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {refresh_token}'
    
    auth = JWTAuthentication()
    with pytest.raises(Exception):
        auth.authenticate(request)

def test_jwt_authentication_deleted_user(request_factory, test_user):
    """בדיקת אימות עם משתמש שנמחק"""
    token = generate_jwt(test_user, 'access')
    test_user.delete()
    
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    auth = JWTAuthentication()
    with pytest.raises(Exception):
        auth.authenticate(request)

def test_jwt_authentication_header_case_insensitive(request_factory, test_user, test_token):
    """בדיקת אימות עם header לא רגיש לאותיות גדולות/קטנות"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {test_token}'
    
    auth = JWTAuthentication()
    result = auth.authenticate(request)
    
    assert result is not None
    assert result[0] == test_user
    assert result[1] is None 