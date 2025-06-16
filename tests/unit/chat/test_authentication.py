import pytest
from django.contrib.auth.models import AnonymousUser
from chat.authentication import JWTAuthentication
from appartners.utils import generate_jwt
from rest_framework import exceptions
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed


def test_jwt_authentication_no_token(request_factory):
    """Test authentication without token"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    
    auth = JWTAuthentication()
    result = auth.authenticate(request)
    
    assert result is None

def test_jwt_authentication_invalid_token(request_factory):
    """Test authentication with invalid token"""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token'
    
    auth = JWTAuthentication()
    with pytest.raises(exceptions.AuthenticationFailed):
        auth.authenticate(request)

@pytest.mark.django_db
def test_jwt_authentication_valid_token(test_user, test_token):
    """Test authentication with a valid token"""
    auth = JWTAuthentication()
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {test_token}'
    
    user_auth_tuple = auth.authenticate(request)
    assert user_auth_tuple is not None
    assert user_auth_tuple[0] == test_user
    assert user_auth_tuple[1] is None  # Token is not returned in the tuple

@pytest.mark.django_db
def test_jwt_authentication_invalid_header_format(test_user):
    """Test authentication with invalid header format"""
    auth = JWTAuthentication()
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = 'InvalidFormat token123'
    
    result = auth.authenticate(request)
    assert result is None  # Invalid format should return None

@pytest.mark.django_db
def test_jwt_authentication_refresh_token(test_user):
    """Test authentication with refresh token"""
    refresh_token = generate_jwt(test_user, 'refresh')
    auth = JWTAuthentication()
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {refresh_token}'
    
    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)

@pytest.mark.django_db
def test_jwt_authentication_deleted_user(test_user, test_token):
    """Test authentication with deleted user"""
    auth = JWTAuthentication()
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {test_token}'
    
    # Delete the user
    test_user.delete()
    
    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)

@pytest.mark.django_db
def test_jwt_authentication_header_case_insensitive(test_user, test_token):
    """Test authentication with case-insensitive header"""
    auth = JWTAuthentication()
    request = RequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = f'bearer {test_token}'
    
    result = auth.authenticate(request)
    assert result is None  # Case-insensitive header should return None 