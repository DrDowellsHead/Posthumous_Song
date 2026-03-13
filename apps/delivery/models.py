from django.contrib.auth.models import User
from django.db import models

from apps.contacts.models import Contact
from apps.messages.models import MessageBundle


class DeliveryJob:
    """ Delivery unit: one contact, one channel, one specific message bundle. """
    owner = models.ForeignKey(User)  # Whose task is delivery
    bundle = models.ForeignKey(MessageBundle)  # What set of messages is sent
    contact = models.ForeignKey(Contact)  # To which recipient is it sent
    channel_type = models.CharField()  # What channel is used: email, telegram, etc.
    status = models.CharField()  # Current status: pending, queued, sent, failed, cancelled
    attempts = models.PositiveIntegerField()  # How many sending attempts have already been made
    scheduled_at = models.DateTimeField()  # When the task should be started
    sent_at = models.DateTimeField()  # When the sending is completed successfully
    last_error = models.TextField()  # Text of the last error
    provider_message_id = models.CharField()  # Message identifier from the external provider
    created_at = models.DateTimeField()  # Created time
    updated_at = models.DateTimeField()  # Updated time
