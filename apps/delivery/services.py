from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_event
from apps.contacts.models import Contact
from apps.delivery.models import DeliveryJob, ReleaseRun
from apps.messages.models import BundleRecipient, MessageAttachment, MessageBundle
from apps.checkins.models import DeadManSwitchState


def choose_delivery_channel(contact: Contact) -> str:
    """
    For now, let's take the preferred_channel.
    ***Will ddd fallback logic here later.***
    """
    if contact.preferred_channel:
        return contact.preferred_channel
    return "email"


def resolve_message_content(bundle: MessageBundle, recipient_link: BundleRecipient) -> tuple[str, str]:
    """
    Selects a topic and text.
    If custom_subject/custom_body is set for a specific recipient,
    they overlap the common fields of bundle.
    """

    subject = recipient_link.custom_subject or bundle.subject or ""
    body = recipient_link.custom_body or bundle.body or ""
    return subject, body


@transaction.atomic
def create_release_jobs_for_user(user) -> int:
    """
    Creates a DeliveryJob for all active message bundles of the user
    and all included recipients.
    Returns the number of tasks created.
    """

    created_jobs = 0

    bundles = MessageBundle.objects.filter(owner=user, is_active=True)

    for bundle in bundles:
        recipient_links = BundleRecipient.objects.select_related("contact").filter(bundle=bundle, is_enabled=True, )

        for recipient_link in recipient_links:
            contact = recipient_link.contact
            channel = choose_delivery_channel(contact)

            # Checking for duplicates
            exiting_job = DeliveryJob.objects.filter(
                owner=user,
                bundle=bundle,
                contact=contact,
                channel_type=channel,
                status__in=["pending", "sent"],
            ).exists()

            if exiting_job:
                continue

            DeliveryJob.objects.create(
                owner=user,
                bundle=bundle,
                contact=contact,
                channel_type=channel,
                status="pending",
                attempts=0,
                scheduled_at=timezone.now(),
            )
            created_jobs += 1

    log_event(
        owner=user,
        event_type="delivery_jobs_created",
        actor_type="system",
        object_type="CustomUser",
        object_id=user.pk,
        payload_json={"created_jobs": created_jobs},
    )

    return created_jobs


def send_email_delivery(job: DeliveryJob) -> DeliveryJob:
    """
    Sends one DeliverJob by email.
    """

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
    """
    A universal dispatcher for one delivery task.
    """

    if job.status == "sent":
        return job

    try:
        if job.channel_type == "email":
            send_email_delivery(job)
        else:
            raise NotImplementedError(f"Канал {job.channel_type!r} пока не реализован.")

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
            object_id=job.pk,
            payload_json={
                "channel_type": job.channel_type,
                "contact_id": job.contact_id,
                "bundle_id": job.bundle_id,
            },
        )
    except Exception as exc:
        job.status = "failed"
        job.attempts += 1
        job.last_error = str(exc)
        job.save(update_fields=["status", "sent_at", "attempts", "last_error", "updated_at"])

        log_event(
            owner=job.owner,
            event_type="delivery_failed",
            actor_type="system",
            object_type="DeliveryJob",
            object_id=job.pk,
            payload_json={
                "channel_type": job.channel_type,
                "error": str(exc),
            },
        )

    return job


@transaction.atomic
def finalize_release_if_completed(user) -> bool:
    """
    If the user has no pending/failed delivery jobs,
    and at least one has been sent, we consider the release complete.
    """

    has_pending_of_failed = DeliveryJob.objects.filter(
        owner=user,
        status__in=["pending", "failed"],
    ).exists()

    has_sent = DeliveryJob.objects.filter(
        owner=user,
        status="sent",
    ).exists()

    if has_pending_of_failed or not has_sent:
        return False

    state = DeadManSwitchState.objects.get(owner=user)
    state.current_status = "released"
    state.save(update_fields=["current_status", "updated_at"])

    log_event(
        owner=user,
        event_type="release_completed",
        actor_type="system",
        object_type="DeadManSwitchState",
        object_id=state.pk,
        payload_json={},
    )

    return True


@transaction.atomic
def start_release_run_for_user(user):
    open_run = ReleaseRun.objects.filter(
        owner=user,
        status=ReleaseRun.STATUS_PENDING,
    ).order_by("-started_at").first()

    if open_run:
        return open_run, False

    run = ReleaseRun.objects.create(
        owner=user,
        status=ReleaseRun.STATUS_PENDING,
    )

    return run, True
