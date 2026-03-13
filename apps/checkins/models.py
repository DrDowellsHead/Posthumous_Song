from django.db import models
from django.contrib.auth.models import AbstractUser, User


class CheckInMethod:
    """ List of ways an international user can ensure his activity. """
    owner = models.ForeignKey(User)  # Who owns the check-in method
    method_type = models.CharField()  # Method type: password, email_link, telegram, desktop_agent, etc.
    is_enabled = models.BooleanField()  # Is this method allowed now
    secret_hash = models.TextField()  # A hash of the secret or token if the method requires a secret value
    metadata_json = models.JSONField()  # Additional method parameters.
    created_at = models.DateTimeField()  # Created time
    updated_at = models.DateTimeField()  # Updated time


class CheckInEvent:
    """ Log of every successful or unsuccessful check-in """
    owner = models.ForeignKey(User)  # Whose check-in was completed
    method_type = models.CharField()  # Through what method did the attempt take place
    is_successful = models.BooleanField()  # The success of the attempt
    ip_address = models.GenericIPAddressField()  # IP address of the request source, if needed for auditing
    user_agent = models.TextField()  # Client information
    created_at = models.DateTimeField()  # Event time


class DeadManSwitchState:
    """ The currently calculated state of the inactivity switch.
    This is a state model from which the scheduler will understand whether it is time to send warnings
    or run a release. """
    owner = models.OneToOneField(User)  # State per user
    last_checkin_at = models.DateTimeField()  # Time of last activity confirmation
    next_deadline_at = models.DateTimeField()  # The date on which the inactivity period expires
    grace_deadline_at = models.DateTimeField()  # End date of grace period
    last_warning_sent_at = models.DateTimeField()  # When was the last time an alert was sent
    current_status = models.CharField()  # Status: active, warning, grace, release_pending, released, paused
    updated_at = models.DateTimeField()  # When was the status last recalculated
