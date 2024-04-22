from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

SINGING_KEY = settings.SIGNING_KEY
def sso_login(username, password):
    return requests.post(
        "https://api.cs.ui.ac.id/authentication/ldap/v2/",
        data={"username": username, "password": password}
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['name'] = user.first_name+" "+user.last_name
    refresh['email'] = user.email
    refresh['username'] = user.username
    decoded_data = jwt.decode(jwt=str(refresh.access_token),
                                key=SINGING_KEY,
                                algorithms="HS512"
                                )
    print(decoded_data)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }