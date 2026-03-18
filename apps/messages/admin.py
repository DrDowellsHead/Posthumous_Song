from django.contrib import admin
from .models import MessageBundle, MessageAttachment, BundleRecipient

admin.site.register(MessageBundle)
admin.site.register(MessageAttachment)
admin.site.register(BundleRecipient)
