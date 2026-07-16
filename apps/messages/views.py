from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BundleRecipientForm, MessageBundleForm
from .models import BundleRecipient, MessageBundle


@login_required
def bundle_list_view(request):
    bundles = MessageBundle.objects.filter(owner=request.user).order_by("-updated_at", "-created_at")

    context = {
        "bundles": bundles,
    }
    return render(request, "messages/bundle_list.html", context)


@login_required
def bundle_create_view(request):
    if request.method == "POST":
        form = MessageBundleForm(request.POST)
        if form.is_valid():
            bundle = form.save(commit=False)
            bundle.owner = request.user
            bundle.save()

            django_messages.success(request, f"Набор сообщений «{bundle.title}» создан.")
            return redirect("posthumous_messages:list")
    else:
        form = MessageBundleForm()

    context = {
        "form": form,
        "page_title": "Новый набор сообщений",
        "submit_label": "Создать набор",
    }
    return render(request, "messages/bundle_form.html", context)


@login_required
def bundle_update_view(request, pk):
    bundle = get_object_or_404(MessageBundle, pk=pk, owner=request.user)

    if request.method == "POST":
        form = MessageBundleForm(request.POST, instance=bundle)
        if form.is_valid():
            form.save()
            django_messages.success(request, f"Набор сообщений «{bundle.title}» обновлён.")
            return redirect("posthumous_messages:list")
        else:
            form = MessageBundleForm(instance=bundle)

        context = {
            "form": form,
            "bundle": bundle,
            "page_title": f"Редактирование: {bundle.title}",
            "submit_label": "Сохранить изменения",
        }
        return render(request, "messages/bundle_form.html", context)


@login_required
def bundle_recipient_view(request, pk):
    bundle = get_object_or_404(MessageBundle, pk=pk, owner=request.user)

    if request.method == "POST":
        form = BundleRecipientForm(request.POST, user=request.user, bundle=bundle)
        if form.is_valid():
            recipient_link = form.save(commit=False)
            recipient_link.bundle = bundle
            recipient_link.save()

            django_messages.success(
                request,
                f"Получатель «{recipient_link.contact.full_name}» добавлен в набор «{bundle.title}».",
            )
            return redirect("posthumous_messages:recipients", pk=bundle.pk)
        else:
            form = BundleRecipientForm(user=request.user, bundle=bundle)

        recipient_links = BundleRecipient.objects.select_related("contact").filter(bundle=bundle).order_by(
            "contact__priority_order",
            "contact__full_name",
        )

        context = {
            "bundle": bundle,
            "form": form,
            "recipient_links": recipient_links,
        }
        return render(request, "messages/bundle_recipients.html", context)


@login_required
def recipient_update_view(request, bundle_pk, recipient_pk):
    bundle = get_object_or_404(MessageBundle, pk=bundle_pk, owner=request.user)
    recipient_link = get_object_or_404(BundleRecipient, pk=recipient_pk, bundle=bundle)

    if request.method == "POST":
        form = BundleRecipientForm(
            request.POST,
            instance=recipient_link,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            django_messages.success(request, "Настройки получателя обновлены.")
            return redirect("posthumous_messages:recipients", pk=bundle.pk)
        else:
            form = BundleRecipientForm(instance=recipient_link, user=request.user)

        context = {
            "bundle": bundle,
            "recipient_link": recipient_link,
            "form": form,
            "page_title": f"Редактирование получателя для «{bundle.title}»",
            "submit_label": "Сохранить изменения",
        }
        return render(request, "messages/recipient_form.html", context)


@login_required
@require_POST
def recipient_delete_view(request, bundle_pk, recipient_pk):
    bundle = get_object_or_404(MessageBundle, pk=bundle_pk, owner=request.user)
    recipient_link = get_object_or_404(BundleRecipient, pk=recipient_pk, bundle=bundle)

    contact_name = recipient_link.contact.full_name
    recipient_link.delete()

    django_messages.info(
        request,
        f"Получатель «{contact_name}» удалён из набора «{bundle.title}».",
    )
    return redirect("posthumous_messages:recipients", pk=bundle.pk)
