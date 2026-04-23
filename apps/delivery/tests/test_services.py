from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.checkins.models import DeadManSwitchState
from apps.contacts.models import Contact
from apps.delivery.models import DeliveryJob, ReleaseRun
from apps.delivery.services import (
    finalize_run_if_completed,
    send_delivery_job,
    start_run_for_user,
)
from apps.messages.models import BundleRecipient, MessageBundle
from apps.policies.models import RealisePolicy

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class DeliveryServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            password="testpass123",
            email="author@example.com"
        )

        DeadManSwitchState.objects.create(
            owner=self.user,
            current_status="run_pending",
        )

        RealisePolicy.objects.create(
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

    def test_start_run_for_user_creates_run_and_jobs(self):
        run, created_jobs = start_run_for_user(self.user)

        self.assertEqual(run.owner, self.user)
        self.assertEqual(run.status, ReleaseRun.STATUS_PENDING)
        self.assertEqual(created_jobs, 1)
        self.assertEqual(run.jobs.count(), 1)

    def test_send_delivery_job_marks_job_sent_and_writes_email(self):
        run, _ = start_run_for_user(self.user)
        job = run.jobs.get()

        send_delivery_job(job)
        job.refresh_from_db()

        self.assertEqual(job.status, "sent")
        self.assertEqual(job.attempts, 1)
        self.assertIsNotNone(job.sent_at)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test subject")
        self.assertEqual(mail.outbox[0].to, ["recipient@example.com"])
        self.assertIn("Hello from PosthumousSong", mail.outbox[0].body)

    def test_finalize_run_if_completed_sets_released(self):
        run, _ = start_run_for_user(self.user)
        job = run.jobs.get()

        send_delivery_job(job)
        result = finalize_run_if_completed(run)

        run.refresh_from_db()
        state = DeadManSwitchState.objects.get(owner=self.user)

        self.assertTrue(result)
        self.assertEqual(run.status, ReleaseRun.STATUS_COMPLETED)
        self.assertEqual(state.current_status, "released")

    def test_finalize_run_if_completed_does_not_complete_when_pending_exists(self):
        run, _ = start_run_for_user(self.user)

        result = finalize_run_if_completed(run)

        run.refresh_from_db()
        state = DeadManSwitchState.objects.get(owner=self.user)

        self.assertFalse(result)
        self.assertEqual(run.status, ReleaseRun.STATUS_PENDING)
        self.assertNotEqual(state.current_status, "released")

    def test_old_sent_jobs_do_not_complete_new_run(self):
        old_run = ReleaseRun.objects.create(
            owner=self.user,
            status=ReleaseRun.STATUS_COMPLETED,
            finished_at=timezone.now()
        )
        DeliveryJob.objects.create(
            owner=self.user,
            run=old_run,
            bundle=self.bundle,
            contact=self.contact,
            channel_type="email",
            status="sent",
            attempts=1,
            scheduled_at=timezone.now(),
            sent_at=timezone.now(),
        )

        new_run, _ = start_run_for_user(self.user)

        result = finalize_run_if_completed(new_run)

        new_run.refresh_from_db()
        state = DeadManSwitchState.objects.get(owner=self.user)

        self.assertFalse(result)
        self.assertEqual(new_run.status, ReleaseRun.STATUS_PENDING)
        self.assertNotEqual(state.current_status, "released")
