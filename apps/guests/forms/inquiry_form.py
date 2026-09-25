from django import forms

from apps.guests.models import Guest


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["name", "email", "organization", "phone", "inquiry"]
        labels = {"inquiry": "About your project"}
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@organization.com"}),
            "organization": forms.TextInput(attrs={"autocomplete": "organization", "placeholder": "Company or organization"}),
            "phone": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "placeholder": "Include your country code"}),
            "inquiry": forms.Textarea(attrs={"rows": 6, "placeholder": "Your sector, country, current data and the outcome you need…"}),
        }
