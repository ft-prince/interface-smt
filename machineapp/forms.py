# machineapp/forms.py
from django import forms
from .models import Machine

class MachineLoginForm(forms.Form):
    machine = forms.ModelChoiceField(
        queryset=Machine.objects.all(),
        empty_label="Select a machine"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize the queryset here if needed