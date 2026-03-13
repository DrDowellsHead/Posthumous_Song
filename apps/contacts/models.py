from django.db import models
from django.contrib.auth.models import AbstractUser


class Contact(AbstractUser):
    """ Class for directory of recipients """
    owner = models.ForeignKey()  # Who owns the contact
    full_name = models.CharField()  # Recipient's display name
    relationship_type = models.CharField()  # Communication category: family, friend, partner, lawyer, etc
    email = models.EmailField()  # Email address for delivery by mail.
    telegram_chat_id = models.CharField()  # Telegram chat ID if the recipient is previously connected to the bot.
    phone = models.CharField()  # Phone for future SMS or WhatsApp scenarios.
    preferred_channel = models.CharField()  # Preferred communication channel on MVP.
    priority_order = models.PositiveIntegerField()  # Order of contact when displaying and processing lists.
    is_verified = models.BooleanField()  # Is the communication channel confirmed?
    is_active = models.BooleanField()  # Should the contact be taken into account in future mailings?
    notes = models.TimeField()  # User's service comments about the contact.
    created_at = models.DateTimeField()  # Creation time
    updated_at = models.DateTimeField()  # Updated time
