"""
Comprehensive authentication tests for JWT-based user management.

Tests cover:
- User registration
- Login/logout
- Token refresh and verification
- Protected endpoint access
- Password management
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPassword123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Create an authenticated API client."""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, refresh


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert response.data['user']['email'] == 'newuser@example.com'
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

        # Verify user was created in database
        assert User.objects.filter(username='newuser').exists()

    def test_register_user_password_mismatch(self, api_client):
        """Test registration fails when passwords don't match."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'DifferentPass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_user_duplicate_username(self, api_client, test_user):
        """Test registration fails with duplicate username."""
        data = {
            'username': test_user.username,
            'email': 'different@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_email(self, api_client, test_user):
        """Test registration fails with duplicate email."""
        data = {
            'username': 'differentuser',
            'email': test_user.email,
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_weak_password(self, api_client):
        """Test registration fails with weak password."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_missing_required_fields(self, api_client):
        """Test registration fails with missing required fields."""
        data = {
            'username': 'newuser',
            # Missing email and passwords
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, api_client, test_user):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }

        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client, test_user):
        """Test login fails with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }

        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Test login fails for nonexistent user."""
        data = {
            'username': 'nonexistent',
            'password': 'SomePassword123'
        }

        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_credentials(self, api_client):
        """Test login fails with missing credentials."""
        data = {
            'username': 'testuser'
            # Missing password
        }

        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenOperations:
    """Test JWT token operations."""

    def test_token_refresh_success(self, api_client, authenticated_client):
        """Test successful token refresh."""
        _, refresh = authenticated_client

        data = {
            'refresh': str(refresh)
        }

        response = api_client.post('/api/auth/token/refresh/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_invalid(self, api_client):
        """Test token refresh fails with invalid token."""
        data = {
            'refresh': 'invalid_token'
        }

        response = api_client.post('/api/auth/token/refresh/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_verify_valid(self, api_client, authenticated_client):
        """Test token verification with valid token."""
        client, refresh = authenticated_client

        data = {
            'token': str(refresh.access_token)
        }

        response = api_client.post('/api/auth/token/verify/', data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_token_verify_invalid(self, api_client):
        """Test token verification with invalid token."""
        data = {
            'token': 'invalid_token'
        }

        response = api_client.post('/api/auth/token/verify/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoint."""

    def test_get_profile_authenticated(self, authenticated_client, test_user):
        """Test getting profile when authenticated."""
        client, _ = authenticated_client

        response = client.get('/api/auth/profile/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == test_user.username
        assert response.data['email'] == test_user.email
        assert response.data['first_name'] == test_user.first_name
        assert response.data['last_name'] == test_user.last_name

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated."""
        response = api_client.get('/api/auth/profile/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, authenticated_client):
        """Test updating user profile."""
        client, _ = authenticated_client

        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }

        response = client.patch('/api/auth/profile/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'


@pytest.mark.django_db
class TestPasswordChange:
    """Test password change endpoint."""

    def test_change_password_success(self, authenticated_client, test_user):
        """Test successful password change."""
        client, _ = authenticated_client

        data = {
            'old_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'new_password_confirm': 'NewPassword456'
        }

        response = client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_200_OK

        # Verify new password works
        test_user.refresh_from_db()
        assert test_user.check_password('NewPassword456')

    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change fails with wrong old password."""
        client, _ = authenticated_client

        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword456',
            'new_password_confirm': 'NewPassword456'
        }

        response = client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch(self, authenticated_client):
        """Test password change fails when new passwords don't match."""
        client, _ = authenticated_client

        data = {
            'old_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'new_password_confirm': 'DifferentPassword'
        }

        response = client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self, api_client):
        """Test password change requires authentication."""
        data = {
            'old_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'new_password_confirm': 'NewPassword456'
        }

        response = api_client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    """Test logout endpoint."""

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        client, refresh = authenticated_client

        data = {
            'refresh': str(refresh)
        }

        response = client.post('/api/auth/logout/', data, format='json')

        assert response.status_code == status.HTTP_200_OK

        # Verify token is blacklisted (can't be refreshed)
        refresh_response = client.post(
            '/api/auth/token/refresh/',
            {'refresh': str(refresh)},
            format='json'
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_missing_token(self, authenticated_client):
        """Test logout fails without refresh token."""
        client, _ = authenticated_client

        response = client.post('/api/auth/logout/', {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client):
        """Test logout requires authentication."""
        data = {
            'refresh': 'some_token'
        }

        response = api_client.post('/api/auth/logout/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""

    def test_patient_list_requires_auth(self, api_client):
        """Test patient list endpoint requires authentication."""
        response = api_client.get('/fhir/Patient/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patient_list_with_auth(self, authenticated_client):
        """Test patient list endpoint works with authentication."""
        client, _ = authenticated_client

        response = client.get('/fhir/Patient/')

        # Should return 200 (with empty list or patients if seeded)
        assert response.status_code == status.HTTP_200_OK

    def test_patient_create_requires_auth(self, api_client):
        """Test patient create endpoint requires authentication."""
        data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Test', 'given': ['Patient']}],
            'gender': 'male',
            'birthDate': '1990-01-01'
        }

        response = api_client.post('/fhir/Patient/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patient_create_with_auth(self, authenticated_client):
        """Test patient create endpoint works with authentication."""
        client, _ = authenticated_client

        data = {
            'resourceType': 'Patient',
            'active': True,
            'name': [{
                'use': 'official',
                'family': 'Test',
                'given': ['Patient']
            }],
            'gender': 'male',
            'birthDate': '1990-01-01',
            'telecom': [{
                'system': 'email',
                'value': 'test@example.com'
            }]
        }

        response = client.post('/fhir/Patient/', data, format='json')

        # Should create successfully
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestAuthenticationSecurity:
    """Test security aspects of authentication."""

    def test_password_not_in_response(self, api_client):
        """Test that password is never returned in API responses."""
        data = {
            'username': 'secureuser',
            'email': 'secure@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123'
        }

        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'password' not in str(response.data)

    def test_tokens_are_different(self, api_client, test_user):
        """Test that access and refresh tokens are different."""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }

        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['access'] != response.data['refresh']

    def test_old_token_invalid_after_logout(self, authenticated_client):
        """Test that tokens are invalid after logout."""
        client, refresh = authenticated_client

        # Get the access token before logout
        access_token = str(refresh.access_token)

        # Logout
        logout_response = client.post(
            '/api/auth/logout/',
            {'refresh': str(refresh)},
            format='json'
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # Try to use the old access token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = client.get('/api/auth/profile/')

        # The token should still work for access until it expires
        # But the refresh token should be blacklisted
        refresh_response = client.post(
            '/api/auth/token/refresh/',
            {'refresh': str(refresh)},
            format='json'
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
