# authentication/settings.py
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os

def get_setting(setting_name, default=None, required=False):
    """Get setting from Django settings with optional default and required check"""
    value = getattr(settings, setting_name, default)
    if required and value is None:
        raise ImproperlyConfigured(f"Setting {setting_name} is required")
    return value

# Keycloak Configuration
KEYCLOAK_CERTS_URL = get_setting('KEYCLOAK_CERTS_URL', required=True)
KEYCLOAK_ISSUER_URL = get_setting('KEYCLOAK_ISSUER_URL', required=True)
KEYCLOAK_AUDIENCE = get_setting('KEYCLOAK_AUDIENCE', 'account')
KEYCLOAK_KEYS_CACHE_TIMEOUT = get_setting('KEYCLOAK_KEYS_CACHE_TIMEOUT', 3600)

# Middleware Configuration
KEYCLOAK_EXEMPT_PATHS = get_setting('KEYCLOAK_EXEMPT_PATHS', [
    '/admin/',
    '/health/',
    '/api/auth/',
])

# Optional settings
KEYCLOAK_AUTO_CREATE_USERS = get_setting('KEYCLOAK_AUTO_CREATE_USERS', True)
KEYCLOAK_UPDATE_USER_INFO = get_setting('KEYCLOAK_UPDATE_USER_INFO', True)
KEYCLOAK_SYNC_ROLES = get_setting('KEYCLOAK_SYNC_ROLES', True)