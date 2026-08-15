from django import forms

from apps.guests.models import Guest


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = [
            "name",
            "email",
            "organization",
            "phone",
            "inquiry",
        ]
