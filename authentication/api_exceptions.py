from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class ExistingUsernameException(BaseCustomException):
    def __init__(self):
        detail = 'Username already exists'
        super().__init__(detail, status.HTTP_409_CONFLICT)

class ExistingEmailException(BaseCustomException):
    def __init__(self):
        detail = 'Email already exists'
        super().__init__(detail, status.HTTP_409_CONFLICT)

class ExistingCourseException(BaseCustomException):
    def __init__(self):
        detail = 'Course already exists'
        super().__init__(detail, status.HTTP_409_CONFLICT)

class ChangePasswordException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
        

class InvalidTokenException(BaseCustomException):
    def __init__(self):
        detail = 'Invalid Token'
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
