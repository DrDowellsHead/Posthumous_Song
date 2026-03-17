from django.db import models
from django.conf import settings


class RealisePolicy(models.Model):
    """ Dead-man switch behavior settings. """
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name="release_policy")  # Whose promotion policy
    inactivity_days = models.PositiveIntegerField(
        default=30)  # After how many days without check-in does an alarming scenario begin
    grace_days = models.PositiveIntegerField(default=7)  # How many days does the grace period last before release
    reminder_schedule_json = models.JSONField(default=dict,
                                              blank=True)  # When exactly to send reminders within inactivity and grace
    auto_release_enabled = models.BooleanField(default=True)  # Is automatic release allowed without manual intervention
    require_guardians_confirmation = models.BooleanField(
        default=False)  # Preparation for the future for a regime with proxies
    created_at = models.DateTimeField(auto_now_add=True)  # Created time
    updated_at = models.DateTimeField(auto_now=True)  # Updated time
