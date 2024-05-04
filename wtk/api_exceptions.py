from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class ExistingWtkException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(detail, status.HTTP_409_CONFLICT)

class WtkPollNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Wtk poll not found", status.HTTP_404_NOT_FOUND)

class WtkReflectionNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__("Wtk reflection not found", status.HTTP_404_NOT_FOUND)

class WtkDoesNotExistException(BaseCustomException):
    def __init__(self):
        super().__init__("Wtk does not exist", status.HTTP_404_NOT_FOUND)

class PrereadingDoesNotExistException(BaseCustomException):
    def __init__(self):
        super().__init__("Prereading not found", status.HTTP_404_NOT_FOUND)

class PrereadingAlreadyExistsException(BaseCustomException):
    def __init__(self):
        super().__init__("Prereading already exists", status.HTTP_409_CONFLICT)