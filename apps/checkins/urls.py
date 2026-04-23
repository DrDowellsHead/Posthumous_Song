from django.urls import path

from .views import dashboard_view, perform_checkin_view, process_deadlines_view

app_name = "checkins"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("perform-checkin/", perform_checkin_view, name="perform_checkin"),
    path("process-deadlines/", process_deadlines_view, name="process_deadlines")
]