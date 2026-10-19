from django.urls import path

from .views import LogoutView, RefreshView, SignupView, UserLoginView

urlpatterns = [
    path("signup", SignupView.as_view()),
    path("user/login", UserLoginView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("logout", LogoutView.as_view()),
]