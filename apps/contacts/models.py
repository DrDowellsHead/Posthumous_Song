from django.db import models
from django.conf import settings


class Contact(models.Model):
    """ Class for directory of recipients """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="contacts")  # Who owns the contact
    full_name = models.CharField(max_length=255)  # Recipient's display name
    relationship_type = models.CharField(max_length=255,
                                         blank=True)  # Communication category: family, friend, partner, lawyer, etc
    email = models.EmailField(blank=True)  # Email address for delivery by mail.
    telegram_chat_id = models.CharField(max_length=100,
                                        blank=True)  # Telegram chat ID if the recipient is previously connected to the bot.
    phone = models.CharField(max_length=50, blank=True)  # Phone for future SMS or WhatsApp scenarios.
    preferred_channel = models.CharField(max_length=30, default="email")  # Preferred communication channel on MVP.
    priority_order = models.PositiveIntegerField(default=0)  # Order of contact when displaying and processing lists.
    is_verified = models.BooleanField(default=False)  # Is the communication channel confirmed?
    is_active = models.BooleanField(default=True)  # Should the contact be taken into account in future mailings?
    notes = models.TextField(blank=True)  # User's service comments about the contact.
    created_at = models.DateTimeField(auto_now_add=True)  # Creation time
    updated_at = models.DateTimeField(auto_now=True)  # Updated time

    def __str__(self):
        return self.full_name
