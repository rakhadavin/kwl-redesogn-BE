from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from authentication.models import Lecturer, Student

SINGING_KEY = settings.SIGNING_KEY
def sso_login(username, password):
    return requests.post(
        "https://api.cs.ui.ac.id/authentication/ldap/v2/",
        data={"username": username, "password": password}
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['role'] = user.role
    if user.role == 'lecturer':
        lecturer = Lecturer.objects.get(user=user)
        refresh['lecturer_pk'] = lecturer.pk
    elif user.role == 'student':
        student = Student.objects.get(user=user)
        refresh['student_pk'] = student.pk
 
    decoded_data = jwt.decode(jwt=str(refresh.access_token),
                                key=SINGING_KEY,
                                algorithms="HS512"
                                )
    print(decoded_data)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }