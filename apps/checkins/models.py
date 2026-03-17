from django.db import models
from django.conf import settings


class CheckInMethod(models.Model):
    """ List of ways an international user can ensure his activity. """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="checkins_methods")  # Who owns the check-in method
    method_type = models.CharField(max_length=50)  # Method type: password, email_link, telegram, desktop_agent, etc.
    is_enabled = models.BooleanField(default=True)  # Is this method allowed now
    secret_hash = models.TextField(blank=True)  # A hash of the secret or token if the method requires a secret value
    metadata_json = models.JSONField(default=dict, blank=True)  # Additional method parameters.
    created_at = models.DateTimeField(auto_now_add=True)  # Created time
    updated_at = models.DateTimeField(auto_now=True)  # Updated time


class CheckInEvent(models.Model):
    """ Log of every successful or unsuccessful check-in """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="checkins_events")  # Whose check-in was completed
    method_type = models.CharField(max_length=50)  # Through what method did the attempt take place
    is_successful = models.BooleanField(default=False)  # The success of the attempt
    ip_address = models.GenericIPAddressField(null=True,
                                              blank=True)  # IP address of the request source, if needed for auditing
    user_agent = models.TextField(blank=True)  # Client information
    created_at = models.DateTimeField(auto_now_add=True)  # Event time


class DeadManSwitchState(models.Model):
    """ The currently calculated state of the inactivity switch.
    This is a state model from which the scheduler will understand whether it is time to send warnings
    or run a release. """
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name="switch_state")  # State per user
    last_checkin_at = models.DateTimeField(null=True, blank=True)  # Time of last activity confirmation
    next_deadline_at = models.DateTimeField(null=True, blank=True)  # The date on which the inactivity period expires
    grace_deadline_at = models.DateTimeField(null=True, blank=True)  # End date of grace period
    last_warning_sent_at = models.DateTimeField(null=True, blank=True)  # When was the last time an alert was sent
    current_status = models.CharField(max_length=50,
                                      default="active")  # Status: active, warning, grace, release_pending, released, paused
    updated_at = models.DateTimeField(auto_now=True)  # When was the status last recalculated
