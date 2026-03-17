from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """ Class for general user. """
    display_name = models.CharField(max_length=150, blank=True)  # Name for the interface and notifications
    timezone = models.CharField(max_length=64,
                                default="Europe/Russia")  # User time zone for calculating deadlines and reminders
    last_seen_at = models.DateTimeField(null=True, blank=True)  # The last observed user action in the system
    emergency_pause_until = models.DateTimeField(null=True,
                                                 blank=True)  # Manual pause of the system if the user is temporarily unable to check-in.
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation date
    updated_at = models.DateTimeField(auto_now=True)  # Last modified date

    def __str__(self):
        return self.display_name or self.username
