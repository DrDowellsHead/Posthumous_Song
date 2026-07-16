from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.contacts.models import Contact
from apps.messages.models import BundleRecipient, MessageBundle

User = get_user_model()


class MessageViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            password="testpass123",
            email="author@example.com",
        )

    def test_bundle_list_requires_login(self):
        response = self.client.get(reverse("posthumous_messages:list"))
        self.assertEqual(response.status_code, 302)

    def test_bundle_create(self):
        self.client.login(username="author", password="testpass123")

        response = self.client.post(
            reverse("posthumous_messages:create"),
            data={
                "title": "Main message",
                "subject": "Subject",
                "body": "Body text",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MessageBundle.objects.filter(owner=self.user).count(), 1)

    def test_bundle_update(self):
        bundle = MessageBundle.objects.create(
            owner=self.user,
            title="Old title",
            subject="Old subject",
            body="Old body",
            is_active=True,
        )

        self.client.login(username="author", password="testpass123")

        response = self.client.post(
            reverse("posthumous_messages:update", args=[bundle.pk]),
            data={
                "title": "New title",
                "subject": "New subject",
                "body": "New body",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 302)

        bundle.refresh_from_db()
        self.assertEqual(bundle.title, "New title")

    def test_add_recipient_to_bundle(self):
        contact = Contact.objects.create(
            owner=self.user,
            full_name="Recipient",
            email="r@example.com",
            preferred_channel="email",
            is_active=True,
        )

        bundle = MessageBundle.objects.create(
            owner=self.user,
            title="Bundle",
            subject="Subject",
            body="Body",
            is_active=True,
        )

        self.client.login(username="author", password="testpass123")

        response = self.client.post(
            reverse("posthumous_messages:recipients", args=[bundle.pk]),
            data={
                "contact": contact.pk,
                "custom_subject": "Custom subject",
                "custom_body": "Custom body",
                "is_enabled": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BundleRecipient.objects.filter(bundle=bundle).count(), 1)
