from django.conf import settings
from django.db import models


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
