from django.urls import path

from .views import (
    contact_create_view,
    contact_deactivate_view,
    contact_list_view,
    contact_update_view,
)

app_name = "contacts"

urlpatterns = [
    path("", contact_list_view, name="list"),
    path("new/", contact_create_view, name="create"),
    path("<int:pk>/edit/", contact_update_view, name="update"),
    path("<int:pk>/deactivate/", contact_deactivate_view, name="deactivate")
]
