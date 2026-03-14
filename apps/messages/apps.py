from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messages"
    label = "posthumous_messages"
    verbose_name = "Posthumous messages"
