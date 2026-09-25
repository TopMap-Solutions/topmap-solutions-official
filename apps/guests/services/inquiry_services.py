from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage, EmailMultiAlternatives


INQUIRY_EMAIL = "joshdels@topmapsolutions.com"


def send_inquiry_emails(data):
    """Send inquiry notification to staff and confirmation to customer."""

    # Send email to staff
    notification = EmailMessage(
        subject="Client Inquiry",
        body=f"""
            New Inquiry Received (TopMap Solutions)

            Name: {data["name"]}
            Organization: {data["organization"]}
            Email: {data["email"]}
            Phone: {data["phone"]}

            Inquiry:
            {data["inquiry"]}
            """.strip(),
        from_email=INQUIRY_EMAIL,
        to=[INQUIRY_EMAIL],
        reply_to=[INQUIRY_EMAIL],
    )
    notification.send(fail_silently=False)

    # Send email to customer
    html_message = render_to_string(
        "email/customer_inquiry.html",
        data,
    )

    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="Inquiry Received",
        body=plain_message,
        from_email=INQUIRY_EMAIL,
        to=[data["email"]],
        reply_to=[INQUIRY_EMAIL],
    )

    message.attach_alternative(html_message, "text/html")
    message.send()
