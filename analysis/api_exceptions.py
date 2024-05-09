from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class InvalidTypeException(BaseCustomException):
    def __init__(self):
        detail = 'Invalid type'
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)

class EmptyReflectionException(BaseCustomException):
    def __init__(self):
        detail = 'No reflections found for this topic.'
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)