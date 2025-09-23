from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from urllib.parse import parse_qs  # Fixed import typo
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTParamAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            try:
                validated_token = UntypedToken(token)
                user_id = validated_token.get('user_id')
                user = await get_user(user_id)
                scope["user"] = user if user else AnonymousUser()
            except (InvalidToken, TokenError) as e:
                print(f"JWT validation error: {e}")
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)