from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class ExistingLearnedException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(detail, status.HTTP_409_CONFLICT)

class LearnedQuizNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Learned quiz not found", status.HTTP_404_NOT_FOUND)

class LearnedReflectionNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Learned reflection not found", status.HTTP_404_NOT_FOUND)

class LearnedDoesNotExistException(BaseCustomException):
    def __init__(self):
        super().__init__("Learned does not exist", status.HTTP_404_NOT_FOUND)