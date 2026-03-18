from django.contrib import admin
from .models import CheckInMethod, CheckInEvent, DeadManSwitchState

admin.site.register(CheckInMethod)
admin.site.register(CheckInEvent)
admin.site.register(DeadManSwitchState)
