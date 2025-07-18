# authentication/middleware.py
import logging
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# Import app settings
from .settings import settings as csauth_settings

logger = logging.getLogger(__name__)


class KeycloakJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = csauth_settings.KEYCLOAK_EXEMPT_PATHS

    def __call__(self, request):
        # Skip authentication for exempt paths
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        # Extract token from Authorization header
        token = self.get_token_from_request(request)

        if token:
            # Authenticate user with token
            user = authenticate(request, token=token)
            if user:
                login(request, user)
                logger.debug(f"User {user.username} authenticated via JWT")
            else:
                logger.warning("JWT token authentication failed")
                return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        else:
            # No token provided
            logger.debug("No JWT token provided")
            return JsonResponse({'error': 'Authentication required'}, status=401)

        response = self.get_response(request)
        return response

    def get_token_from_request(self, request):
        """Extract JWT token from Authorization header"""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None