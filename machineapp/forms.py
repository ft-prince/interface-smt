# machineapp/forms.py
from django import forms
from .models import Machine

class MachineLoginForm(forms.Form):
    machine = forms.ModelChoiceField(
        queryset=Machine.objects.filter(is_active=False),
        empty_label="Select a machine"
    )