from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_event
from apps.checkins.models import CheckInEvent, DeadManSwitchState
from apps.delivery.services import start_run_for_user
from apps.policies.models import RealisePolicy


@dataclass
class CheckInResult:
    state: DeadManSwitchState
    event: CheckInEvent
    created_state: bool


def get_or_create_policy(user) -> RealisePolicy:
    policy, _ = RealisePolicy.objects.get_or_create(
        owner=user,
        defaults={
            "inactivity_days": 30,
            "grace_days": 7,
            "auto_release_enabled": True,
            "require_guardians_confirmation": False,
            "reminder_schedule_json": {},
        },
    )
    return policy


def get_or_create_switch_state(user) -> tuple[DeadManSwitchState, bool]:
    state, created = DeadManSwitchState.objects.get_or_create(
        owner=user,
        defaults={
            "current_status": "active",
        },
    )
    return state, created


@transaction.atomic
def perform_checkin(
        *,
        user,
        method_type: str,
        ip_address: str | None = None,
        user_agent: str = "",
) -> CheckInResult:
    now = timezone.now()

    policy = get_or_create_policy(user)
    state, created_state = get_or_create_switch_state(user)

    event = CheckInEvent.objects.create(
        owner=user,
        method_type=method_type,
        is_successful=True,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    next_deadline = now + timedelta(days=policy.inactivity_days)
    grace_deadline = next_deadline + timedelta(days=policy.grace_days)

    state.last_checkin_at = now
    state.next_deadline_at = next_deadline
    state.grace_deadline_at = grace_deadline
    state.current_status = "active"
    state.save(
        update_fields=[
            "last_checkin_at",
            "next_deadline_at",
            "grace_deadline_at",
            "current_status",
            "updated_at",
        ]
    )

    log_event(
        owner=user,
        event_type="checkin_performed",
        actor_type="user",
        object_type="DeadManSwitchState",
        object_id=str(state.pk),
        payload_json={
            "method_type": method_type,
            "next_deadline_at": next_deadline.isoformat(),
            "grace_deadline_at": grace_deadline.isoformat(),
        },
    )

    return CheckInResult(
        state=state,
        event=event,
        created_state=created_state,
    )


@transaction.atomic
def process_deadline_tick() -> int:
    now = timezone.now()
    changed_count = 0

    states = DeadManSwitchState.objects.select_related("owner").all()

    for state in states:
        user = state.owner

        pause_until = getattr(user, "emergency_pause_until", None)
        if pause_until and pause_until > now:
            continue

        if state.current_status == "released":
            continue

        if not state.next_deadline_at:
            continue

        if now < state.next_deadline_at:
            continue

        if state.grace_deadline_at and state.next_deadline_at <= now < state.grace_deadline_at:
            if state.current_status != "grace":
                state.current_status = "grace"
                state.save(update_fields=["current_status", "updated_at"])
                changed_count += 1

                log_event(
                    owner=user,
                    event_type="grace_started",
                    actor_type="system",
                    object_type="DeadManSwitchState",
                    object_id=str(state.pk),
                    payload_json={
                        "next_deadline_at": state.next_deadline_at.isoformat(),
                        "grace_deadline_at": state.grace_deadline_at.isoformat(),
                    },
                )
            continue

        if state.grace_deadline_at and now >= state.grace_deadline_at:
            if state.current_status not in ("run_pending", "released"):
                run, created_jobs = start_run_for_user(user)

                state.current_status = "run_pending"
                state.save(update_fields=["current_status", "updated_at"])
                changed_count += 1

                log_event(
                    owner=user,
                    event_type="run_pending_started",
                    actor_type="system",
                    object_type="DeadManSwitchState",
                    object_id=str(state.pk),
                    payload_json={
                        "run_id": run.pk,
                        "created_jobs": created_jobs,
                        "grace_deadline_at": state.grace_deadline_at.isoformat(),
                    },
                )

    return changed_count
