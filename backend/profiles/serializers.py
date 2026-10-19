from datetime import date

from rest_framework import serializers

from .models import HealthProfile


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = [
            "id", "full_name", "date_of_birth", "contact_preference",
            "wellness_goals", "allergies", "emergency_contact_name",
            "emergency_contact_phone", "lifestyle_notes",
            "status", "created_at", "updated_at",
        ]
        # Users cannot change these; status is admin-controlled.
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name cannot be blank.")
        return value

    def validate_date_of_birth(self, value):
        if value is None:
            return value
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        if value.year < 1900:
            raise serializers.ValidationError("Date of birth is not realistic.")
        return value

class AdminProfileSerializer(HealthProfileSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(HealthProfileSerializer.Meta):
        fields = HealthProfileSerializer.Meta.fields + ["user_email"]    