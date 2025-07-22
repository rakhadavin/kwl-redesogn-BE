from authentication import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from .views import LoginView, RegisterStudentView, StudentDetailView, LogoutView, RegisterTeacherView, LecturerDetailView, ResetPasswordConfirmByTokenView, RequestPasswordResetEmailView, ProviderLoginView


urlpatterns = [
    path("register/student", RegisterStudentView.as_view(), name="student_register"),
    path("register/lecturer", RegisterTeacherView.as_view(), name="teacher_register"),
    path("login", LoginView.as_view(), name="login"),
    path('login/provider', ProviderLoginView.as_view(), name='provider_login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path("student", StudentDetailView.as_view(), name="student_detail"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("lecturer", LecturerDetailView.as_view(), name="lecturer_detail"),
    path('reset-password/<str:token>', ResetPasswordConfirmByTokenView.as_view(), name='reset_password_confirm'),
    path('reset', RequestPasswordResetEmailView.as_view(), name='reset'),
    path('student/all', views.StudentListView.as_view(), name='student_list'),
    path('lecturer/all', views.LecturerListView.as_view(), name='lecturer_list'),
]