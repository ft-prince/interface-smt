# Add this to forms.py if not already there
from django import forms
from .models import Machine

class MachineLoginForm(forms.Form):
    machine = forms.ModelChoiceField(
        queryset=Machine.objects.all(),
        empty_label="Select a machine",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg mb-3',
            'aria-label': 'Select Machine'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get all machines and make sure they're ordered
        self.fields['machine'].queryset = Machine.objects.all().order_by('name')