from django.urls import re_path
from .consumers.teacher_consumer import TeacherConsumer
from .consumers.guest_consumer import GuestConsumer


websocket_urlpatterns = [
    re_path(r'ws/kuesioner/(?P<kuesioner_id>[0-9a-f-]+)/$', TeacherConsumer.as_asgi()),
    re_path(r'ws/kuesioner/guest/(?P<guest_id>[0-9a-f-]+)/$', GuestConsumer.as_asgi()),
]