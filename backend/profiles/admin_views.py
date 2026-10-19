from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HealthProfile
from .serializers import AdminProfileSerializer


class AdminPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class AdminProfileListView(ListAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = AdminProfileSerializer
    pagination_class = AdminPagination
    filter_backends = [SearchFilter]
    search_fields = ["full_name", "user__email"]

    def get_queryset(self):
        qs = HealthProfile.objects.select_related("user").order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param in ("active", "inactive"):
            qs = qs.filter(status=status_param)
        return qs


class AdminProfileDetailView(RetrieveAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = AdminProfileSerializer
    queryset = HealthProfile.objects.select_related("user")


class AdminProfileDeactivateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        profile = get_object_or_404(HealthProfile, pk=pk)
        profile.status = HealthProfile.Status.INACTIVE
        profile.save(update_fields=["status", "updated_at"])
        return Response(AdminProfileSerializer(profile).data)