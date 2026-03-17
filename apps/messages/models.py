from django.db import models
from django.conf import settings

from apps.contacts.models import Contact


class MessageBundle(models.Model):  # Правильное ли наследование я здесь применяю?
    """ Set of messages. This is the logical unit of submission:
    subject, body, activity status, and ownership. """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="messages_bundles")  # The owner of the message
    title = models.CharField(max_length=255)  # Internal name of the set in the interface
    subject = models.CharField(max_length=255, blank=True)  # Email subject or message title
    body = models.TextField()  # Main text of the message
    is_active = models.BooleanField(default=True)  # Is it possible to use bundle during a real release
    created_at = models.DateTimeField(auto_now_add=True)  # Creation time
    updated_at = models.DateTimeField(auto_now=True)  # Updated time

    def __str__(self):
        return self.title


class MessageAttachment(models.Model):
    """ Files attached to MessageBundle. """
    bundle = models.ForeignKey(MessageBundle, on_delete=models.CASCADE,
                               related_name="attachments")  # Which set does the file belong to
    file = models.FileField(upload_to="message_attachments/")  # Path to the file in storage
    attachment_type = models.CharField(max_length=50)  # Category: image, video, document, other.
    original_name = models.CharField(max_length=255)  # The file name that the user sees.
    file_size = models.PositiveIntegerField(default=0)  # File size in bytes.
    created_at = models.DateTimeField(auto_now_add=True)  # When the file was downloaded


class BundleRecipient(models.Model):
    """ The bridging model between MessageBundle and Contact.
    It is needed so that you can send your own version of the text to one contact
    or disable a specific recipient for one specific set. """
    bundle = models.ForeignKey(MessageBundle, on_delete=models.CASCADE,
                               related_name="recipients")  # Which set does the connection belong to
    contact = models.ForeignKey("contacts.Contact", on_delete=models.CASCADE,
                                related_name="message_links")  # To whom is a particular option addressed
    custom_subject = models.CharField(max_length=255, blank=True)  # Individual topic for the recipient
    custom_body = models.TextField(blank=True)  # Personalized text instead of a generic body
    is_enabled = models.BooleanField(default=True)  # Do I need to send the bundle to this particular contact
