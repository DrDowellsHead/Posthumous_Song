import uuid

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class AuditEvent(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="audit_events")  # Whose entity or context is affected by the event
    event_type = models.CharField(max_length=100)  # Event type: login, checkin, contact_created, delivery_failed, etc.
    actor_type = models.CharField(max_length=50)  # Who performed the action: user, system, admin, worker, node
    object_type = models.CharField(max_length=100)  # On what entity the action occurred
    object_id = models.CharField(max_length=64, blank=True)  # Object ID
    payload_json = models.JSONField(default=dict, blank=True)  # Expandable event details
    created_at = models.DateTimeField(auto_now_add=True)  # Created time
