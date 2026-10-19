from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from profiles.models import HealthProfile

User = get_user_model()
PW = "Str0ng!Pass2026"


def make_user(email, name, staff=False):
    u = User.objects.create_user(email=email, password=PW, name=name, is_staff=staff)
    if not staff:
        HealthProfile.objects.create(user=u, full_name=name)
    return u


@pytest.fixture
def user(db):
    return make_user("a@example.com", "User A")


@pytest.fixture
def other(db):
    return make_user("b@example.com", "User B")


@pytest.fixture
def admin(db):
    return make_user("admin@example.com", "Admin", staff=True)


def user_login(client, email="a@example.com", password=PW):
    return client.post("/api/auth/user/login", {"email": email, "password": password}, format="json")


def csrf(client):
    return client.cookies["csrftoken"].value


def admin_client(email="admin@example.com"):
    c = APIClient(enforce_csrf_checks=True)
    c.get("/api/admin/csrf")
    r = c.post("/api/admin/login", {"email": email, "password": PW},
               format="json", HTTP_X_CSRFTOKEN=csrf(c))
    return c, r


# ---------- signup ----------
def test_signup_valid(db):
    r = APIClient().post("/api/auth/signup",
                         {"name": "New", "email": "new@example.com", "password": PW}, format="json")
    assert r.status_code == 201
    assert "password" not in r.data
    assert HealthProfile.objects.filter(user__email="new@example.com").exists()


def test_signup_password_is_hashed(db):
    APIClient().post("/api/auth/signup",
                     {"name": "New", "email": "new@example.com", "password": PW}, format="json")
    assert User.objects.get(email="new@example.com").password != PW


def test_signup_weak_password(db):
    r = APIClient().post("/api/auth/signup",
                         {"name": "X", "email": "x@example.com", "password": "123"}, format="json")
    assert r.status_code == 400


def test_signup_invalid_email(db):
    r = APIClient().post("/api/auth/signup",
                         {"name": "X", "email": "not-an-email", "password": PW}, format="json")
    assert r.status_code == 400


def test_signup_duplicate_email_case_insensitive(user):
    r = APIClient().post("/api/auth/signup",
                         {"name": "Dup", "email": "A@EXAMPLE.COM", "password": PW}, format="json")
    assert r.status_code == 400


# ---------- user login ----------
def test_login_sets_httponly_cookies(user):
    r = user_login(APIClient())
    assert r.status_code == 200
    assert r.cookies["access_token"]["httponly"]
    assert r.cookies["refresh_token"]["httponly"]


def test_login_wrong_password(user):
    assert user_login(APIClient(), password="wrong").status_code == 401


def test_staff_cannot_use_user_login(admin):
    assert user_login(APIClient(), email="admin@example.com").status_code == 401


# ---------- JWT validity ----------
def test_profile_without_token(db):
    assert APIClient().get("/api/profiles/me").status_code == 401


def test_profile_with_tampered_token(user):
    c = APIClient()
    c.cookies["access_token"] = "abc.def.ghi"
    assert c.get("/api/profiles/me").status_code == 401


def test_profile_with_expired_token(user):
    token = AccessToken.for_user(user)
    token.set_exp(from_time=timezone.now() - timedelta(hours=1), lifetime=timedelta(minutes=1))
    c = APIClient()
    c.cookies["access_token"] = str(token)
    assert c.get("/api/profiles/me").status_code == 401


def test_staff_jwt_rejected_on_profile_route(admin):
    c = APIClient()
    c.cookies["access_token"] = str(AccessToken.for_user(admin))
    assert c.get("/api/profiles/me").status_code == 401


# ---------- profile access and validation ----------
def test_user_reads_own_profile_only(user, other):
    c = APIClient()
    user_login(c)
    r = c.get("/api/profiles/me")
    assert r.status_code == 200 and r.data["full_name"] == "User A"


def test_no_route_to_other_users_profile(user, other):
    c = APIClient()
    user_login(c)
    assert c.get(f"/api/profiles/{other.profile.id}").status_code == 404


def test_patch_own_profile_does_not_touch_other(user, other):
    c = APIClient()
    user_login(c)
    r = c.patch("/api/profiles/me", {"wellness_goals": "Sleep more"}, format="json")
    assert r.status_code == 200
    other.profile.refresh_from_db()
    assert other.profile.wellness_goals == ""


def test_patch_future_dob_rejected(user):
    c = APIClient()
    user_login(c)
    assert c.patch("/api/profiles/me", {"date_of_birth": "2999-01-01"}, format="json").status_code == 400


def test_patch_blank_name_rejected(user):
    c = APIClient()
    user_login(c)
    assert c.patch("/api/profiles/me", {"full_name": "  "}, format="json").status_code == 400


def test_user_cannot_change_status(user):
    c = APIClient()
    user_login(c)
    c.patch("/api/profiles/me", {"status": "inactive"}, format="json")
    user.profile.refresh_from_db()
    assert user.profile.status == "active"


# ---------- admin: separation of the two auth paths ----------
def test_user_jwt_cannot_reach_admin_routes(user):
    c = APIClient()
    user_login(c)
    assert c.get("/api/admin/profiles").status_code == 403


def test_normal_user_cannot_admin_login(user):
    _, r = admin_client(email="a@example.com")
    assert r.status_code == 401


def test_admin_login_requires_csrf(admin):
    c = APIClient(enforce_csrf_checks=True)
    r = c.post("/api/admin/login", {"email": "admin@example.com", "password": PW}, format="json")
    assert r.status_code == 403


def test_admin_list_requires_login(db):
    assert APIClient().get("/api/admin/profiles").status_code == 403


def test_admin_list_and_search(admin, user, other):
    c, r = admin_client()
    assert r.status_code == 200
    assert c.get("/api/admin/profiles").data["count"] == 2
    found = c.get("/api/admin/profiles", {"search": '"User A"'})
    assert found.data["count"] == 1


def test_admin_filter_by_status(admin, user, other):
    other.profile.status = "inactive"
    other.profile.save()
    c, _ = admin_client()
    assert c.get("/api/admin/profiles?status=inactive").data["count"] == 1


def test_admin_deactivate(admin, user):
    c, _ = admin_client()
    r = c.patch(f"/api/admin/profiles/{user.profile.id}/deactivate", HTTP_X_CSRFTOKEN=csrf(c))
    assert r.status_code == 200
    user.profile.refresh_from_db()
    assert user.profile.status == "inactive"


def test_admin_logout_kills_session(admin):
    c, _ = admin_client()
    assert c.post("/api/admin/logout", HTTP_X_CSRFTOKEN=csrf(c)).status_code == 200
    assert c.get("/api/admin/profiles").status_code == 403


def test_admin_logout_requires_csrf(admin):
    c, _ = admin_client()
    assert c.post("/api/admin/logout").status_code == 403