from apps.audit.models import AuditEvent


def log_event(*, owner, event_type: str, actor_type: str, object_type: str, object_id,
              payload_json: dict[str, object] | None = None) -> AuditEvent:
    """
    Creates an entry in AuditEvent

    :param owner: - event owner user
    :param event_type: - event type, for example 'checkin_performed'
    :param actor_type: - who performed the action: 'user', 'system', 'scheduler'
    :param object_type: - what the action happened on: 'DeadManSwitchState', 'DeliveryJob'
    :param object_id: - object id
    :param payload_json: - additional data
    :return: - AuditEvent

    """

    return AuditEvent.objects.create(owner=owner, event_type=event_type, actor_type=actor_type, object_type=object_type,
                                    object_id=object_id, payload_json=payload_json or {}, )
