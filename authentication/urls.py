from authentication import views
from django.urls import path

from .views import LoginView, RegisterStudentView

urlpatterns = [
    path("register/", RegisterStudentView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    # path("logout/", LogoutView.as_view(), name="logout_view"),
    # path("user/", UserDetailsView.as_view(), name="user_details")
]