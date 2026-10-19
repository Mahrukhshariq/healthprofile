from django.conf import settings
from django.db import models


class HealthProfile(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    class ContactPreference(models.TextChoices):
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        SMS = "sms", "SMS"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_preference = models.CharField(
        max_length=10, choices=ContactPreference.choices, default=ContactPreference.EMAIL
    )
    wellness_goals = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    lifestyle_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # admin list: filter by status, newest first
            models.Index(fields=["status", "-created_at"], name="idx_profile_status_created"),
            # admin search by name
            models.Index(fields=["full_name"], name="idx_profile_full_name"),
        ]

    def __str__(self):
        return self.full_name