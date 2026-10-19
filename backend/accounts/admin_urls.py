from django.urls import path

from profiles.admin_views import (
    AdminProfileDeactivateView,
    AdminProfileDetailView,
    AdminProfileListView,
)

from .admin_views import AdminLoginView, AdminLogoutView, CsrfView

urlpatterns = [
    path("csrf", CsrfView.as_view()),
    path("login", AdminLoginView.as_view()),
    path("logout", AdminLogoutView.as_view()),
    path("profiles", AdminProfileListView.as_view()),
    path("profiles/<int:pk>", AdminProfileDetailView.as_view()),
    path("profiles/<int:pk>/deactivate", AdminProfileDeactivateView.as_view()),
]