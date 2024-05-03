from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class ExistingKnowException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(detail, status.HTTP_409_CONFLICT)


class KnowQuizNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Know quiz not found", status.HTTP_404_NOT_FOUND)

class KnowReflectionNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Know reflection not found", status.HTTP_404_NOT_FOUND)


class KnowDoesNotExistException(BaseCustomException):
    def __init__(self):
        super().__init__("Know does not exist", status.HTTP_404_NOT_FOUND)