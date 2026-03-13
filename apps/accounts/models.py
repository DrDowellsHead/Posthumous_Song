from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """ Class for general user. """
    email = models.EmailField()  # Unique login and main user contact
    display_name = models.CharField()  # Name for the interface and notifications
    timezone = models.CharField()  # User time zone for calculating deadlines and reminders
    is_active = models.BooleanField()  # Standard account activity flag
    is_staff = models.BooleanField()  # Access to Django admin
    last_seen_at = models.DateTimeField()  # The last observed user action in the system
    emergency_pause_until = models.DateTimeField()  # Manual pause of the system if the user is temporarily unable to check-in.
    created_at = models.DateTimeField()  # Record creation date
    updated_at = models.DateTimeField()  # Last modified date
