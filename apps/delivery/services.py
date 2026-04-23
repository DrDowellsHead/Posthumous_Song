from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_event
from apps.checkins.models import DeadManSwitchState
from apps.contacts.models import Contact
from apps.delivery.models import DeliveryJob, ReleaseRun
from apps.messages.models import BundleRecipient, MessageAttachment, MessageBundle


def choose_delivery_channel(contact: Contact) -> str:
    if contact.preferred_channel:
        return contact.preferred_channel
    return "email"


def resolve_message_content(bundle: MessageBundle, recipient_link: BundleRecipient) -> tuple[str, str]:
    subject = recipient_link.custom_subject or bundle.subject or ""
    body = recipient_link.custom_body or bundle.body or ""
    return subject, body


@transaction.atomic
def start_run_for_user(user):
    open_run = ReleaseRun.objects.filter(
        owner=user,
        status=ReleaseRun.STATUS_PENDING,
    ).order_by("-started_at").first()

    if open_run:
        return open_run, 0

    run = ReleaseRun.objects.create(
        owner=user,
        status=ReleaseRun.STATUS_PENDING,
    )

    created_jobs = _create_jobs_for_run(run)

    log_event(
        owner=user,
        event_type="run_started",
        actor_type="system",
        object_type="ReleaseRun",
        object_id=str(run.pk),
        payload_json={"created_jobs": created_jobs},
    )

    return run, created_jobs


def _create_jobs_for_run(run) -> int:
    user = run.owner
    created_jobs = 0

    bundles = MessageBundle.objects.filter(owner=user, is_active=True)

    for bundle in bundles:
        recipient_links = BundleRecipient.objects.select_related("contact").filter(
            bundle=bundle,
            is_enabled=True,
        )

        for recipient_link in recipient_links:
            contact = recipient_link.contact
            channel = choose_delivery_channel(contact)

            existing_job = DeliveryJob.objects.filter(
                run=run,
                bundle=bundle,
                contact=contact,
                channel_type=channel,
            ).exists()

            if existing_job:
                continue

            DeliveryJob.objects.create(
                owner=user,
                run=run,
                bundle=bundle,
                contact=contact,
                channel_type=channel,
                status="pending",
                attempts=0,
                scheduled_at=timezone.now(),
            )
            created_jobs += 1

    return created_jobs


def send_email_delivery(job: DeliveryJob) -> DeliveryJob:
    recipient_link = BundleRecipient.objects.get(
        bundle=job.bundle,
        contact=job.contact,
    )

    subject, body = resolve_message_content(job.bundle, recipient_link)

    if not job.contact.email:
        raise ValueError("The contact does not have an email for delivery.")

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[job.contact.email],
    )

    attachments = MessageAttachment.objects.filter(bundle=job.bundle)
    for attachment in attachments:
        email.attach_file(attachment.file.path)

    email.send(fail_silently=False)
    return job


@transaction.atomic
def send_delivery_job(job: DeliveryJob) -> DeliveryJob:
    if job.status == "sent":
        return job

    try:
        if job.channel_type == "email":
            send_email_delivery(job)
        else:
            raise NotImplementedError(f"Channel {job.channel_type!r} is not implemented yet.")

        job.status = "sent"
        job.sent_at = timezone.now()
        job.attempts += 1
        job.last_error = ""
        job.save(update_fields=["status", "sent_at", "attempts", "last_error", "updated_at"])

        log_event(
            owner=job.owner,
            event_type="delivery_sent",
            actor_type="system",
            object_type="DeliveryJob",
            object_id=str(job.pk),
            payload_json={
                "run_id": job.run_id,
                "channel_type": job.channel_type,
                "contact_id": job.contact_id,
                "bundle_id": job.bundle_id,
            },
        )

    except Exception as exc:
        job.status = "failed"
        job.attempts += 1
        job.last_error = str(exc)
        job.save(update_fields=["status", "attempts", "last_error", "updated_at"])

        log_event(
            owner=job.owner,
            event_type="delivery_failed",
            actor_type="system",
            object_type="DeliveryJob",
            object_id=str(job.pk),
            payload_json={
                "run_id": job.run_id,
                "channel_type": job.channel_type,
                "error": str(exc),
            },
        )

    return job


@transaction.atomic
def finalize_run_if_completed(run) -> bool:
    jobs = run.jobs.all()

    if not jobs.exists():
        run.status = ReleaseRun.STATUS_EMPTY
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at"])
        return False

    if jobs.exclude(status="sent").exists():
        return False

    run.status = ReleaseRun.STATUS_COMPLETED
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "finished_at"])

    state = DeadManSwitchState.objects.get(owner=run.owner)
    state.current_status = "released"
    state.save(update_fields=["current_status", "updated_at"])

    log_event(
        owner=run.owner,
        event_type="run_completed",
        actor_type="system",
        object_type="ReleaseRun",
        object_id=str(run.pk),
        payload_json={},
    )

    return True
