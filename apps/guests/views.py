from datetime import timedelta
from django.http import HttpResponse

from django.shortcuts import redirect, render
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives

from .models import Guest


def homepage(request):
    return render(request, "homepage.html")


def inquiry_page(request):
    return render(request, "inquiry.html")


def inquiry_form(request):
    return render(request, "form/contact.html")


def send_public_form(request):
    if request.method != "POST":
        return redirect("inquiry")

    name = request.POST.get("name", "")
    email = request.POST.get("email", "")
    organization = request.POST.get("organization", "Individual")
    phone = request.POST.get("phone", "")
    inquiry = request.POST.get("inquiry", "")

    cooldown = Guest.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(hours=24),
    ).exists()

    if cooldown:
        return render(
            request,
            "inquiry.html",
            {
                "error": "You have already submitted an inquiry within the last 24 hours.",
                "name": name,
                "organization": organization,
                "email": email,
                "phone": phone,
                "inquiry": inquiry,
            },
        )

    # Send email to staff
    send_mail(
        subject="Client Inquiry",
        message=f"""
            New Inquiry Received (TopMap Solutions)

            Name: {name}
            Organization: {organization}
            Email: {email}
            Phone: {phone}

            Inquiry:
            {inquiry}

            """.strip(),
        from_email="noreply@topmapsolutions.com",
        recipient_list=["joshdels@topmapsolutions.com"],
        fail_silently=False,
    )

    # Send email to customer
    html_message = render_to_string(
        "email/customer_inquiry.html",
        {
            "name": name,
            "email": email,
            "phone": phone,
            "organization": organization,
            "inquiry": inquiry,
        },
    )
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="Inquiry Received",
        body=plain_message,
        from_email="noreply@topmapsolutions.com",
        to=[email],
    )

    message.attach_alternative(html_message, "text/html")
    message.send()

    # Send to database
    Guest.objects.create(
        name=name, email=email, organization=organization, phone=phone, inquiry=inquiry
    )

    request.session["submitted_email"] = email
    return redirect("inquiry_success")


def inquiry_success(request):
    email = request.session.pop("submitted_email", None)

    if not email:
        return redirect("inquiry")

    return render(
        request,
        "contact_success.html",
        {"email": email},
    )


def test(request):
    return HttpResponse("Hello1")
