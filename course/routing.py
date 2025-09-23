from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r"ws/course/(?P<course_id>\d+)/(?P<topic_id>\d+)/$", consumers.CourseNotificationConsumer.as_asgi()),
]