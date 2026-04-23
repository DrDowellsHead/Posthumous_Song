from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.checkins.models import CheckInEvent, DeadManSwitchState
from apps.checkins.services import perform_checkin, process_deadline_tick
from apps.contacts.models import Contact
from apps.delivery.models import DeliveryJob, ReleaseRun
from apps.messages.models import BundleRecipient, MessageBundle
from apps.policies.models import RealisePolicy

User = get_user_model()


class CheckinServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            password="testpass123",
            email="author@example.com",
        )

        self.policy = RealisePolicy.objects.create(
            owner=self.user,
            inactivity_days=30,
            grace_days=7,
            reminder_schedule_json={},
            auto_release_enabled=True,
            require_guardians_confirmation=False,
        )

        self.contact = Contact.objects.create(
            owner=self.user,
            full_name="Recipient One",
            email="recipient@example.com",
            preferred_channel="email",
            is_active=True,
        )

        self.bundle = MessageBundle.objects.create(
            owner=self.user,
            title="Main bundle",
            subject="Test subject",
            body="Hello from PosthumousSong",
            is_active=True,
        )

        BundleRecipient.objects.create(
            bundle=self.bundle,
            contact=self.contact,
            custom_subject="",
            custom_body="",
            is_enabled=True,
        )

    def test_perform_checkin_creates_event_and_updates_state(self):
        result = perform_checkin(user=self.user, method_type="web")

        state = DeadManSwitchState.objects.get(owner=self.user)

        self.assertEqual(result.state.pk, state.pk)
        self.assertEqual(state.current_status, "active")
        self.assertIsNotNone(state.last_checkin_at)
        self.assertIsNotNone(state.next_deadline_at)
        self.assertIsNotNone(state.grace_deadline_at)

        self.assertEqual(CheckInEvent.objects.filter(owner=self.user).count(), 1)

    def test_process_deadline_tick_starts_run_and_creates_jobs(self):
        now = timezone.now()

        DeadManSwitchState.objects.create(
            owner=self.user,
            last_checkin_at=now - timedelta(days=40),
            next_deadline_at=now - timedelta(days=10),
            grace_deadline_at=now - timedelta(days=1),
            current_status="active",
        )

        changed = process_deadline_tick()

        state = DeadManSwitchState.objects.get(owner=self.user)
        run = ReleaseRun.objects.get(owner=self.user)

        self.assertEqual(changed, 1)
        self.assertEqual(state.current_status, "run_pending")
        self.assertEqual(run.status, ReleaseRun.STATUS_PENDING)
        self.assertEqual(run.jobs.count(), 1)
        self.assertEqual(
            DeliveryJob.objects.filter(owner=self.user, run=run).count(),
            1
        )

    def test_process_deadline_tick_moves_to_grace(self):
        now = timezone.now()

        DeadManSwitchState.objects.create(
            owner=self.user,
            last_checkin_at=now - timedelta(days=35),
            next_deadline_at=now - timedelta(days=1),
            grace_deadline_at=now + timedelta(days=3),
            current_status="active",
        )

        changed = process_deadline_tick()

        state = DeadManSwitchState.objects.get(owner=self.user)

        self.assertEqual(changed, 1)
        self.assertEqual(state.current_status, "grace")
        self.assertEqual(ReleaseRun.objects.filter(owner=self.user).count(), 0)
