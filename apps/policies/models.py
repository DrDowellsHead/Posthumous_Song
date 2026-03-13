from django.db import models
from django.contrib.auth.models import User


class RealisePolicy:
    """ Dead-man switch behavior settings. """
    owner = models.OneToOneField(User)  # Whose promotion policy
    inactivity_days = models.PositiveIntegerField()  # After how many days without check-in does an alarming scenario begin
    grace_days = models.PositiveIntegerField()  # How many days does the grace period last before release
    reminder_schedule_json = models.JSONField()  # When exactly to send reminders within inactivity and grace
    auto_release_enabled = models.BooleanField()  # Is automatic release allowed without manual intervention
    require_guardians_confirmation = models.BooleanField()  # Preparation for the future for a regime with proxies
    created_at = models.DateTimeField()  # Created time
    updated_at = models.DateTimeField()  # Updated time


