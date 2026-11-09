from django import forms

from .models import Account


class ImportForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    file = forms.FileField(help_text="Trading 212 history export (CSV)")
