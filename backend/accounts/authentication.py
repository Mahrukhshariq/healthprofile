from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Reads the access JWT from an HttpOnly cookie. Rejects staff accounts,
    so an admin can never use the user-JWT path."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None
        validated = self.get_validated_token(raw_token)
        user = self.get_user(validated)
        if user.is_staff:
            raise AuthenticationFailed("Admin accounts must use the admin session login.")
        return user, validated