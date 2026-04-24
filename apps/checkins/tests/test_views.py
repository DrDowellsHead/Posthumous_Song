from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.checkins.models import CheckInEvent, DeadManSwitchState
from apps.policies.models import RealisePolicy

from apps.contacts.models import Contact

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

    def test_contact_create(self):
        self.client.login(username="author", password="testpass123")

        response = self.client.post(
            reverse("contacts:create"),
            data={
                "full_name": "Test Contact",
                "relationship_type": "friend",
                "email": "test@example.com",
                "telegram_chat_id": "",
                "phone": "",
                "preferred_channel": "email",
                "priority_order": 1,
                "is_verified": True,
                "is_active": True,
                "notes": "note",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contact.objects.filter(owner=self.user).count(), 1)

    def test_contact_update(self):
        contact = Contact.objects.create(
            owner=self.user,
            full_name="Old Name",
            email="old@example.com",
            preferred_channel="email",
        )

        self.client.login(username="author", password="testpass123")

        response = self.client.post(
            reverse("contacts:update", args=[contact.pk]),
            data={
                "full_name": "New Name",
                "relationship_type": "",
                "email": "new@example.com",
                "telegram_chat_id": "",
                "phone": "",
                "preferred_channel": "email",
                "priority_order": 0,
                "is_verified": False,
                "is_active": True,
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        contact.refresh_from_db()
        self.assertEqual(contact.full_name, "New Name")
        self.assertEqual(contact.email, "new@example.com")

    def test_contact_deactivate(self):
        contact = Contact.objects.create(
            owner=self.user,
            full_name="To Disable",
            email="x@example.com",
            preferred_channel="email",
            is_active=True,
        )

        self.client.login(username="author", password="testpass123")

        response = self.client.post(reverse("contacts:deactivate", args=[contact.pk]))
        self.assertEqual(response.status_code, 302)

        contact.refresh_from_db()
        self.assertFalse(contact.is_active)
