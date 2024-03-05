import requests
from rest_framework_simplejwt.tokens import RefreshToken

def sso_login(username, password):
    return requests.post(
        "https://api.cs.ui.ac.id/authentication/ldap/v2/",
        data={"username": username, "password": password}
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }