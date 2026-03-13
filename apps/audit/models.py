from django.contrib.auth.models import User
from django.db import models


class AuditEvent:
    owner = models.ForeignKey(User)  # Whose entity or context is affected by the event
    event_type = models.CharField()  # Event type: login, checkin, contact_created, delivery_failed, etc.
    actor_type = models.CharField()  # Who performed the action: user, system, admin, worker, node
    object_type = models.CharField()  # On what entity the action occurred
    object_id = models.UUIDField()  # Object ID
    payload_json = models.JSONField()  # Expandable event details
    created_at = models.DateTimeField()  # Created time
