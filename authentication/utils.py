from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from rest_framework.views import exception_handler
from authentication.models import Lecturer, Student

SINGING_KEY = settings.SIGNING_KEY
def sso_login(username, password):
    return requests.post(
        "https://api.cs.ui.ac.id/authentication/ldap/v2/",
        data={"username": username, "password": password}
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    refresh['username'] = user.username
    refresh['role'] = user.role
    refresh['name'] = user.first_name + ' ' + user.last_name
   
    if user.role == 'lecturer':
        lecturer = Lecturer.objects.get(user=user)
        refresh['lecturer_pk'] = lecturer.pk
    elif user.role == 'student':
        student = Student.objects.get(user=user)
        refresh['student_pk'] = student.pk
    else:
        refresh['student_pk'] = None
        refresh['lecturer_pk'] = None

    decoded_data = jwt.decode(jwt=str(refresh.access_token),
                                key=SINGING_KEY,
                                algorithms="HS512"
                                )
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if 'detail' in response.data:
            response.data['message'] = response.data['detail']
            del response.data['detail']
    return response


