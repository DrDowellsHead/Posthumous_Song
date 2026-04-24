from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ContactForm
from .models import Contact


@login_required
def contact_list_view(request):
    contacts = Contact.objects.filter(owner=request.user).order_by("priority_order", "full_name")

    context = {
        "contacts": contacts,
    }
    return render(request, "contacts/contact_list.html", context)


@login_required
def contact_create_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()

            django_messages.success(request, f"Контакт «{contact.full_name}» создан.")
            return redirect("contacts:list")
    else:
        form = ContactForm()

    context = {
        "form": form,
        "page_title": "Новый Контакт",
        "submit_label": "Создать Контакт",
    }
    return render(request, "contacts/contact_form.html", context)


@login_required
def contact_update_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            django_messages.success(request, f"Контакт «{contact.full_name}» обновлён.")
            return redirect("contacts:list")
    else:
        form = ContactForm(instance=contact)

    context = {
        "form": form,
        "contact": contact,
        "page_title": f"Редактирование: {contact.full_name}",
        "submit_label": "Сохранить изменения",
    }
    return render(request, "contacts/contact_form.html", context)


@login_required
@require_POST
def contact_deactivate_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)

    contact.is_active = False
    contact.save(update_fields=["is_active", "updated_at"])

    django_messages.info(request, f"Контакт «{contact.full_name}» деактивирован.")
    return redirect("contacts:list")
