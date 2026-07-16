from django import forms

from apps.contacts.models import Contact
from .models import BundleRecipient, MessageBundle


class MessageBundleForm(forms.ModelForm):
    class Meta:
        model = MessageBundle
        fields = [
            "title",
            "subject",
            "body",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Основное Послание"}),
            "subject": forms.TextInput(attrs={"placeholder": "Тема Письма"}),
            "body": forms.Textarea(attrs={"rows": 10, "placeholder": "Текст Сообщения"}),
        }


class BundleRecipientForm(forms.ModelForm):
    class Meta:
        model = BundleRecipient
        fields = [
            "contact",
            "custom_subject",
            "custom_body",
            "is_enabled",
        ]
        widgets = {
            "custom_subject": forms.TextInput(attrs={"placeholder": "Переопределение темы для этого контакта"}),
            "custom_body": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Переопределение текста для этого контакта"}),
        }

        def __init__(self, *args, user=None, bundle=None, **kwargs):
            super().__init__(*args, **kwargs)

            if user is not None:
                self.fields["contact"].queryset = Contact.objects.filter(
                    owner=user,
                    is_active=True,
                ).order_by("priority_order", "full_name")

            if bundle is not None and self.instance.pk is None:
                user_contact_ids = BundleRecipient.objects.filter(bundle=bundle).values_list("contact_id", flat=True)
                self.fields["contact"].queryset = self.fields["contact"].queryset.exclude(pk_in=user_contact_ids)
