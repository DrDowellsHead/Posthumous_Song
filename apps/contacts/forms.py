from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "full_name",
            "relationship_type",
            "email",
            "telegram_chat_id",
            "phone",
            "preferred_channel",
            "priority_order",
            "is_verified",
            "is_active",
            "notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Дон Жуан"}),
            "relationship_type": forms.TextInput(attrs={"placeholder": "Family / Friend / Colleague"}),
            "email": forms.EmailInput(attrs={"placeholder": "recipient@example.com"}),
            "telegram_chat_id": forms.TextInput(attrs={"placeholder": "chat_id"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7..."}),
            "preferred_channel": forms.Select(
                choices=[
                    ("email", "Email"),
                    ("telegram", "Telegram"),
                    ("sms", "SMS"),
                    ("whatsapp", "WhatsApp"),
                ]
            ),
            "priority_order": forms.NumberInput(attrs={"min": 0}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Комментарии о контакте"}),
        }
