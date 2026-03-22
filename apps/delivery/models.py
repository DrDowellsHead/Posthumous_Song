from django.conf import settings
from django.db import models


class ReleaseRun(models.Model):
    """
    Represents a single release attempt for a user's posthumous messages.

    A release run is created when the system decides that message delivery
    must begin, typically after the inactivity deadline and grace period
    have both expired.

    This model groups all DeliveryJob records that belong to the same release
    cycle. It allows the system to distinguish the current release attempt
    from previous ones and prevents incorrect completion checks based on
    old delivery jobs.

    Responsibilities:
    - identify one concrete release cycle;
    - store the lifecycle status of that cycle;
    - group all delivery jobs created for that cycle;
    - provide a reliable unit for completion and failure checks.

    Typical lifecycle:
    1. A ReleaseRun is created with status = "pending".
    2. DeliveryJob objects are created and attached to the run.
    3. Jobs are processed by delivery services.
    4. The run is finalized as "completed", "failed", or "empty".

    Status meanings:
    - pending: the release has started and is still in progress;
    - completed: all jobs in this run were successfully delivered;
    - failed: one or more jobs failed and the run did not complete cleanly;
    - empty: the run was started, but no delivery jobs were created.

    Relations:
    - owner: the user whose messages are being released;
    - jobs: all DeliveryJob objects created for this run.
    """

    STATUS_PENDING = "pending"  # the release has been started, tasks have been created or are still being created
    STATUS_COMPLETED = "completed"  # all tasks of this release have been successfully completed
    STATUS_FAILED = "failed"  # release completed with errors
    STATUS_EMPTY = "empty"  # the release was created, but there were no tasks to submit

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_EMPTY, "Empty"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="release_runs",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ReleaseRun #{self.pk} for {self.owner}"


class DeliveryJob(models.Model):
    """ Delivery unit: one contact, one channel, one specific message bundle. """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="delivery_jobs")  # Whose task is delivery
    bundle = models.ForeignKey("posthumous_messages.MessageBundle", on_delete=models.CASCADE,
                               related_name="delivery_jobs")  # What set of messages is sent
    contact = models.ForeignKey("contacts.Contact", on_delete=models.CASCADE,
                                related_name="delivery_jobs")  # To which recipient is it sent
    channel_type = models.CharField(max_length=30)  # What channel is used: email, telegram, etc.
    status = models.CharField(max_length=30,
                              default="pending")  # Current status: pending, queued, sent, failed, cancelled
    attempts = models.PositiveIntegerField(default=0)  # How many sending attempts have already been made
    scheduled_at = models.DateTimeField()  # When the task should be started
    sent_at = models.DateTimeField(null=True, blank=True)  # When the sending is completed successfully
    last_error = models.TextField(blank=True)  # Text of the last error
    provider_message_id = models.CharField(max_length=255, blank=True)  # Message identifier from the external provider
    created_at = models.DateTimeField(auto_now_add=True)  # Created time
    updated_at = models.DateTimeField(auto_now=True)  # Updated time
