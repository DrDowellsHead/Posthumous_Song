from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from apps.checkins.models import CheckInEvent
from apps.checkins.services import get_or_create_policy, get_or_create_switch_state, perform_checkin, \
    process_deadline_tick
from apps.contacts.models import Contact
from apps.delivery.models import DeliveryJob, ReleaseRun
from apps.messages.models import MessageBundle


def get_client_ip(request) -> str | None:
    """
    Retrieve the real client IP address from a Django HTTP request.

    This function handles cases where the request passes through proxies or load balancers
    by prioritizing the 'X-Forwarded-For' header (which may contain a comma-separated list
    of IPs, with the first one being the original client). If not present, it falls back
    to the 'REMOTE_ADDR' which is the direct IP seen by the server.

    Args:
        request (django.http.HttpRequest): The Django request object containing META headers.

    Returns:
        str | None: The client IP address as a string (e.g., '192.168.1.1'), or None if unavailable.

    Example:
        >>> get_client_ip(request)
        '203.0.113.42'
    """

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


@login_required
def dashboard_view(request):
    user = request.user

    policy = get_or_create_policy(user)
    state, _ = get_or_create_switch_state(user)

    contacts = Contact.objects.filter(owner=user, is_active=True).order_by("full_name")
    bundles = MessageBundle.objects.filter(owner=user, is_active=True).order_by("-created_at")
    last_run = ReleaseRun.objects.filter(owner=user).order_by("-started_at").first()
    recent_checkins = CheckInEvent.objects.filter(owner=user).order_by("-created_at")[:5]

    pending_jobs_count = DeliveryJob.objects.filter(owner=user, status="pending").count()
    failed_jobs_count = DeliveryJob.objects.filter(owner=user, status="failed").count()
    sent_jobs_count = DeliveryJob.objects.filter(owner=user, status="sent").count()

    context = {
        "policy": policy,
        "state": state,
        "contacts": contacts,
        "bundles": bundles,
        "last_run": last_run,
        "recent_checkins": recent_checkins,
        "pending_jobs_count": pending_jobs_count,
        "failed_jobs_count": failed_jobs_count,
        "sent_jobs_count": sent_jobs_count,
    }
    return render(request, "checkins/dashboard.html", context)


@login_required
def perform_checkin_view(request):
    if request.method != "POST":
        return redirect("checkins:dashboard")

    result = perform_checkin(
        user=request.user,
        method_type="web",
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    next_deadline = result.state.next_deadline_at
    if next_deadline:
        django_messages.success(
            request,
            f"Активность подтверждена. Следующий дедлайн: {next_deadline:%d.%m.%Y %H:%M}",
        )
    else:
        django_messages.success(request, "Активность подтверждена.")

    return redirect("checkins:dashboard")


@login_required
def process_deadlines_view(request):
    if request.method != "POST":
        return redirect("checkins:dashboard")

    if not request.user.is_staff:
        return HttpResponseForbidden("Только сотрудники могут вручную запускать обработку сроков.")

    changed_count = process_deadline_tick()

    django_messages.info(
        request,
        f"Проверка дедлайнов завершена. Изменённых состояний: {changed_count}.",
    )
    return redirect("checkins:dashboard")
