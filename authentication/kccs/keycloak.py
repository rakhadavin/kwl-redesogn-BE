# authentication/keycloak.py
import jwt
import json
import base64
import requests
import logging
from datetime import datetime, timedelta
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Import app settings
from . import settings as csauth_settings

logger = logging.getLogger(__name__)
User = get_user_model()


class KeycloakJWTBackend(BaseBackend):
    def __init__(self):
        self.keycloak_certs_url = csauth_settings.KEYCLOAK_CERTS_URL
        self.issuer_url = csauth_settings.KEYCLOAK_ISSUER_URL
        self.audience = csauth_settings.KEYCLOAK_AUDIENCE
        self.cache_timeout = csauth_settings.KEYCLOAK_KEYS_CACHE_TIMEOUT
        self.auto_create_users = csauth_settings.KEYCLOAK_AUTO_CREATE_USERS
        self.update_user_info = csauth_settings.KEYCLOAK_UPDATE_USER_INFO
        self.sync_roles = csauth_settings.KEYCLOAK_SYNC_ROLES

    def load_public_keys(self):
        """Fetch and cache public keys from Keycloak"""
        cache_key = 'keycloak_jwks_data'
        cached_jwks = cache.get(cache_key)

        if cached_jwks:
            # Convert cached JWK data back to RSA keys
            return self._jwks_to_rsa_keys(cached_jwks)

        try:
            response = requests.get(self.keycloak_certs_url, timeout=10)
            response.raise_for_status()

            jwks = response.json()

            # Cache the raw JWKS data (which is serializable)
            cache.set(cache_key, jwks, self.cache_timeout)
            logger.info(f"Cached JWKS data from Keycloak")

            # Convert to RSA keys and return
            return self._jwks_to_rsa_keys(jwks)

        except requests.RequestException as e:
            logger.error(f"Failed to fetch keys from Keycloak: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error processing keys: {e}")
            return {}

    def _jwks_to_rsa_keys(self, jwks):
        """Convert JWKS data to RSA key objects"""
        keys = {}

        for key in jwks.get('keys', []):
            if key.get('use') == 'sig' and key.get('kty') == 'RSA':
                kid = key['kid']
                try:
                    rsa_key = self.jwk_to_rsa_key(key)
                    keys[kid] = rsa_key
                except Exception as e:
                    logger.warning(f"Failed to convert key {kid}: {e}")

        logger.info(f"Converted {len(keys)} JWKS keys to RSA keys")
        return keys

    def jwk_to_rsa_key(self, jwk):
        """Convert JWK to RSA public key"""
        try:
            n = base64.urlsafe_b64decode(jwk['n'] + '==')
            e = base64.urlsafe_b64decode(jwk['e'] + '==')

            n_int = int.from_bytes(n, 'big')
            e_int = int.from_bytes(e, 'big')

            public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
            public_key = public_numbers.public_key(backend=default_backend())

            return public_key
        except Exception as e:
            logger.error(f"Error converting JWK to RSA key: {e}")
            raise

    def verify_token(self, token):
        """Verify JWT token and return decoded payload"""
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')

            if not kid:
                logger.warning("Token missing 'kid' in header")
                return None

            # Get public keys
            keys = self.load_public_keys()
            public_key = keys.get(kid)

            if not public_key:
                logger.warning(f"Public key not found for kid: {kid}")
                # Try refreshing keys once
                cache.delete('keycloak_jwks_data')
                keys = self.load_public_keys()
                public_key = keys.get(kid)

                if not public_key:
                    logger.error(f"Public key still not found for kid: {kid} after refresh")
                    return None

            # Verify and decode token
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=self.audience,
                issuer=self.issuer_url,
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_signature": True
                },
                leeway=timedelta(seconds=60)
            )

            return decoded

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None

    # ... rest of your existing methods remain the same ...

    def authenticate(self, request, token=None):
        """Authenticate user based on JWT token"""
        if not token:
            return None

        # Verify token
        payload = self.verify_token(token)
        if not payload:
            return None

        # Extract user info from token
        user_id = payload.get('sub')
        username = payload.get('preferred_username')
        email = payload.get('email')
        first_name = payload.get('given_name', '')
        last_name = payload.get('family_name', '')

        if not user_id or not username:
            logger.warning("Token missing required user information")
            return None

        # Get or create user
        try:
            user = User.objects.get(username=username)
            # Update user info if configured to do so
            if self.update_user_info:
                self._update_user_from_token(user, payload)
        except User.DoesNotExist:
            if not self.auto_create_users:
                logger.warning(f"User {username} not found and auto-creation is disabled")
                return None

            # Create new user
            user = self._create_user_from_token(payload)
            logger.info(f"Created new user: {username}")

        # Store token payload in user object for access in views
        user.keycloak_payload = payload
        return user

    def _create_user_from_token(self, payload):
        """Create user from token payload"""
        user_data = {
            'username': payload.get('preferred_username'),
            'email': payload.get('email', ''),
            'first_name': payload.get('given_name', ''),
            'last_name': payload.get('family_name', ''),
        }

        # If using custom KeycloakUser model
        if hasattr(User, 'keycloak_id'):
            user_data['keycloak_id'] = payload.get('sub')

        user = User.objects.create_user(**user_data)

        # Update additional Keycloak data
        if hasattr(user, 'update_from_keycloak'):
            user.update_from_keycloak(payload)

        return user

    def _update_user_from_token(self, user, payload):
        """Update user info from token payload"""
        updated = False

        email = payload.get('email', '')
        first_name = payload.get('given_name', '')
        last_name = payload.get('family_name', '')

        if user.email != email:
            user.email = email
            updated = True
        if user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if user.last_name != last_name:
            user.last_name = last_name
            updated = True

        if updated:
            user.save()

        # Update Keycloak-specific data
        if hasattr(user, 'update_from_keycloak'):
            user.update_from_keycloak(payload)

    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None