from django.db import models
from django.contrib.auth.models import AbstractUser, User

from apps.contacts.models import Contact


class MessageBundle(User):  # Правильное ли наследование я здесь применяю?
    """ Set of messages. This is the logical unit of submission:
    subject, body, activity status, and ownership. """
    owner = models.ForeignKey(User)  # The owner of the message
    title = models.CharField()  # Internal name of the set in the interface
    subject = models.CharField()  # Email subject or message title
    body = models.TextField()  # Main text of the message
    is_active = models.BooleanField()  # Is it possible to use bundle during a real release
    created_at = models.DateTimeField()  # Creation time
    updated_at = models.DateTimeField()  # Updated time


class MessageAttachment:
    """ Files attached to MessageBundle. """
    bundle = models.ForeignKey(MessageBundle)  # Which set does the file belong to
    file = models.FileField()  # Path to the file in storage
    attachment_type = models.CharField()  # Category: image, video, document, other.
    original_name = models.CharField()  # The file name that the user sees.
    file_size = models.PositiveIntegerField()  # File size in bytes.
    created_at = models.DateTimeField()  # When the file was downloaded


class BundleRecipient:
    """ The bridging model between MessageBundle and Contact.
    It is needed so that you can send your own version of the text to one contact
    or disable a specific recipient for one specific set. """
    bundle = models.ForeignKey(MessageBundle)  # Which set does the connection belong to
    contact = models.ForeignKey(Contact)  # To whom is a particular option addressed
    custom_subject = models.CharField()  # Individual topic for the recipient
    custom_body = models.TextField()  # Personalized text instead of a generic body
    is_enabled = models.BooleanField()  # Do I need to send the bundle to this particular contact
