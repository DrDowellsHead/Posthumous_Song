from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.checkins.models import CheckInEvent, DeadManSwitchState
from apps.policies.models import RealisePolicy

User = get_user_model()


class CheckinViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            password="testpass123",
            email="author@example.com",
        )

        RealisePolicy.objects.create(
            owner=self.user,
            inactivity_days=30,
            grace_days=7,
            reminder_schedule_json={},
            auto_release_enabled=True,
            require_guardians_confirmation=False,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("checkins:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_logged_user(self):
        self.client.login(username="author", password="testpass123")
        response = self.client.get(reverse("checkins:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PosthumousSong")

    def test_post_checkin_creates_event(self):
        self.client.login(username="author", password="testpass123")

        response = self.client.post(reverse("checkins:perform_checkin"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CheckInEvent.objects.filter(owner=self.user).count(), 1)
        self.assertTrue(DeadManSwitchState.objects.filter(owner=self.user).exists())
