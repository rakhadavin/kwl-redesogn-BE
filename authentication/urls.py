from authentication import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import LoginView, RegisterStudentView, StudentDetailView

urlpatterns = [
    path("register/student", RegisterStudentView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("student/", StudentDetailView.as_view(), name="student_detail"),
    # path("lecturer/<int:pk>", DetailLecturerView.as_view(), name="lecturer_detail")
]