from django.urls import path

from .views import (
    bundle_create_view,
    bundle_list_view,
    bundle_recipient_view,
    bundle_update_view,
    recipient_update_view,
    recipient_delete_view,
)

app_name = "posthumous_messages"

urlpatterns = [
    path("", bundle_list_view, name="list"),
    path("new/", bundle_create_view, name="create"),
    path("<int:pk>/edit/", bundle_update_view, name="update"),
    path("<int:pk>/recipients/", bundle_recipient_view, name="recipients"),
    path("<int:bundle_pk>/recipients/<int:recipient_pk>/edit/", recipient_update_view, name="recipient_update"),
    path("<int:bundle_pk>/recipients/<int:recipient_pk>/delete/", recipient_delete_view, name="recipient_delete"),
]
