from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from profiles.models import HealthProfile

SEED = [
    ("Sara Malik", "sara.malik@example.com", "1994-03-12", "email", "Improve sleep routine", "Pollen", "Hina Malik", "+1-555-0101", "active"),
    ("Omar Siddiqui", "omar.siddiqui@example.com", "1988-07-25", "phone", "Run a 10k", "", "Zain Siddiqui", "+1-555-0102", "active"),
    ("Layla Hassan", "layla.hassan@example.com", "2000-11-02", "sms", "Eat more vegetables", "Peanuts", "Amal Hassan", "+1-555-0103", "active"),
    ("Daniel Reyes", "daniel.reyes@example.com", "1979-01-30", "email", "Reduce screen time", "", "Maria Reyes", "+1-555-0104", "active"),
    ("Mei Tanaka", "mei.tanaka@example.com", "1991-09-18", "phone", "Daily 20 min stretching", "Shellfish", "Ken Tanaka", "+1-555-0105", "inactive"),
    ("Ayesha Khan", "ayesha@example.com", "1996-05-05", "phone", "Walk 30 minutes daily", "", "Fatima Khan", "+1-555-0106", "active"),
]
DEMO_PASSWORD = "Demo!Pass2026"  # fictional demo accounts only


class Command(BaseCommand):
    help = "Create synthetic demo users and profiles (fictional data only)."

    def handle(self, *args, **options):
        User = get_user_model()
        for name, email, dob, pref, goals, allergies, ec_name, ec_phone, status in SEED:
            user, created = User.objects.get_or_create(email=email, defaults={"name": name})
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            HealthProfile.objects.update_or_create(
                user=user,
                defaults=dict(
                    full_name=name, date_of_birth=dob, contact_preference=pref,
                    wellness_goals=goals, allergies=allergies,
                    emergency_contact_name=ec_name, emergency_contact_phone=ec_phone,
                    status=status,
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(SEED)} synthetic profiles."))