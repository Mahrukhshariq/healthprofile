import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the admin account from ADMIN_EMAIL / ADMIN_PASSWORD env vars."

    def handle(self, *args, **options):
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        if not email or not password:
            raise CommandError("Set ADMIN_EMAIL and ADMIN_PASSWORD in .env")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email.lower(), defaults={"name": "Admin"}
        )
        user.is_staff = True
        user.set_password(password)  # hashed
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Admin {'created' if created else 'updated'}: {user.email}"
        ))