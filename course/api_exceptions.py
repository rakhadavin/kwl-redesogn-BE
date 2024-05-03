from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code

class CourseNotFoundException(BaseCustomException):
    def __init__(self):
        detail = 'Course not found'
        super().__init__(detail, status.HTTP_404_NOT_FOUND)

class TopicNotFoundException(BaseCustomException):
    def __init__(self):
        detail = 'Topic not found'
        super().__init__(detail, status.HTTP_404_NOT_FOUND)

class RewardNotFoundException(BaseCustomException):
    def __init__(self):
        detail = 'Reward not found'
        super().__init__(detail, status.HTTP_404_NOT_FOUND)