from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from profiles.models import HealthProfile

from .serializers import LoginSerializer, SignupSerializer

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"


def set_cookie(response, name, value, max_age, path="/"):
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=True,                 # JS cannot read it (XSS protection)
        secure=not settings.DEBUG,     # HTTPS only in production
        samesite="Lax",                # CSRF protection
        path=path,
    )


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        HealthProfile.objects.create(user=user, full_name=user.name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["email"].lower(),
            password=serializer.validated_data["password"],
        )
        # Same message for every failure so attackers can't probe emails.
        if user is None or user.is_staff:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)  # claims: user id only, no secrets
        response = Response({"id": user.id, "name": user.name, "email": user.email})
        set_cookie(response, ACCESS_COOKIE, str(refresh.access_token),
                   max_age=15 * 60)
        set_cookie(response, REFRESH_COOKIE, str(refresh),
                   max_age=7 * 24 * 3600, path="/api/auth/")
        return response


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE)
        if not token:
            return Response({"detail": "No refresh token."},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(token)
            access = str(refresh.access_token)
        except TokenError:
            return Response({"detail": "Invalid or expired refresh token."},
                            status=status.HTTP_401_UNAUTHORIZED)
        response = Response({"detail": "Token refreshed."})
        set_cookie(response, ACCESS_COOKIE, access, max_age=15 * 60)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Logged out."})
        response.delete_cookie(ACCESS_COOKIE, path="/")
        response.delete_cookie(REFRESH_COOKIE, path="/api/auth/")
        return response