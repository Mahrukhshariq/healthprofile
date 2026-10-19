from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.authentication import CookieJWTAuthentication

from .models import HealthProfile
from .serializers import HealthProfileSerializer


class MyProfileView(RetrieveUpdateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HealthProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]  # PATCH = partial update

    def get_object(self):
        # Always the logged-in user's own profile. No id from the URL.
        profile, _ = HealthProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"full_name": self.request.user.name},
        )
        return profile