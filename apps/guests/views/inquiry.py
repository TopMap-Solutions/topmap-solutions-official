from django.shortcuts import redirect, render

from apps.guests.models import Guest
from apps.guests.selectors import check_email_cooldown
from apps.guests.forms import InquiryForm
from apps.guests.services import send_inquiry_emails


def inquiry_form(request):
    return render(request, "form/contact.html")


def inquiry_success(request):
    email = request.session.pop("submitted_email", None)

    if not email:
        return redirect("inquiry")

    return render(
        request,
        "contact_success.html",
        {"email": email},
    )


def send_public_form(request):
    if request.method != "POST":
        return redirect("inquiry")

    form = InquiryForm(request.POST)

    if not form.is_valid():
        return render(request, "inquiry.html", {"form": form})

    data = form.cleaned_data

    if check_email_cooldown(data["email"]):
        form.add_error(
            "email",
            "You have already submitted an inquiry within the last 24 hours.",
        )

        return render(
            request,
            "inquiry.html",
            {"form": form},
        )

    send_inquiry_emails(data)

    Guest.objects.create(**data)

    request.session["submitted_email"] = data["email"]

    return redirect("inquiry_success")
