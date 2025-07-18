# authentication/authentication.py
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .keycloak import KeycloakJWTBackend
from ..models import Student

logger = logging.getLogger(__name__)
User = get_user_model()


class KeycloakJWTAuthentication(BaseAuthentication):
    """
    DRF Authentication class for Keycloak JWT tokens
    """
    keyword = 'Bearer'

    def __init__(self):
        self.backend = KeycloakJWTBackend()

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = self.get_authorization_header(request)
        if not auth_header:
            return None

        token = self.get_token_from_header(auth_header)
        if not token:
            return None

        return self.authenticate_credentials(token, request)

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth

    def get_token_from_header(self, auth_header):
        """
        Extract token from Authorization header
        """
        auth = auth_header.split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        return token

    def authenticate_credentials(self, token, request):
        """
        Authenticate the token and return user
        """
        try:
            # Verify token using Keycloak backend
            payload = self.backend.verify_token(token)
            if not payload:
                raise AuthenticationFailed('Invalid or expired token.')

            # Get or create user
            user = self.get_or_create_user(payload)
            if not user:
                raise AuthenticationFailed('User not found or could not be created.')

            # Store token payload for access in views
            user.keycloak_payload = payload

            return (user, token)

        except Exception as e:
            logger.warning(f"Token authentication failed: {e}")
            raise AuthenticationFailed('Invalid token.')

    def get_or_create_user(self, payload):
        """
        Get or create user from JWT payload
        """
        user_id = payload.get('sub')
        username = payload.get('preferred_username')

        if not user_id or not username:
            logger.warning("Token missing required user information")
            return None

        try:
            user = User.objects.get(username=username)
            # Update user info if configured
            if self.backend.update_user_info:
                self.backend._update_user_from_token(user, payload)
        except User.DoesNotExist:
            if not self.backend.auto_create_users:
                logger.warning(f"User {username} not found and auto-creation is disabled")
                return None

            user = self.backend._create_user_from_token(payload)
            logger.info(f"Created new user: {username}")

        return user

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return f'{self.keyword} realm="api"'
