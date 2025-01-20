from django import forms
from .models import Screen

class ScreenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ['video_path', 'pdf_path']  # Include the file path fields you want to customize

    def __init__(self, *args, **kwargs):
        super(ScreenForm, self).__init__(*args, **kwargs)
        # Customize the file path fields here if needed
        
        
#----------------------------------------------------------------
#  FixtureCleaningRecordForm
from .models import FixtureCleaningRecord

class FixtureCleaningRecordForm(forms.ModelForm):
    class Meta:
        model = FixtureCleaningRecord
        fields = '__all__'
        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'fixture_installation_date': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

# forms.py
from django import forms

class FixtureCleaningRecordSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fixture_location = forms.ChoiceField(choices=[('', 'All')] + FixtureCleaningRecord.FIXTURE_LOCATION, required=False)
    shift = forms.ChoiceField(choices=[('', 'All')] + FixtureCleaningRecord.SHIFT_CHOICES, required=False)
    verification_status = forms.ChoiceField(
        choices=[('', 'All'), ('Available', 'Available'), ('Not Available', 'Not Available')],
        required=False
    )
    fixture_control_no = forms.CharField(required=False)
#----------------------------------------------------------------
# RejectionSheetForm
from .models import RejectionSheet,STATION_CHOICES

class RejectionSheetForm(forms.ModelForm):
    class Meta:
        model = RejectionSheet
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class RejectionSheetSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    station = forms.ChoiceField(choices=[('', 'All')] + STATION_CHOICES, required=False)  # Use the imported STATION_CHOICES
    stage = forms.ChoiceField(choices=[('', 'All')] + RejectionSheet.STAGE_CHOICES, required=False)
    part_description = forms.ChoiceField(choices=[('', 'All')] + STATION_CHOICES, required=False)  # Assuming part_description uses STATION_CHOICES
# ----------------------------------------------------------------

from .models import SolderingBitRecord 

class SolderingBitRecordForm(forms.ModelForm):
    class Meta:
        model = SolderingBitRecord
        fields = [
            'station', 'doc_number', 'part_name', 'machine_no', 'machine_location',
            'month', 'time', 'soldering_points_per_part', 'bit_size', 'date',
            'produce_quantity_shift_a', 'produce_quantity_shift_b', 'bit_change_date',
            'prepared_by', 'approved_by'
        ]
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'bit_change_date': forms.DateInput(attrs={'type': 'date'}),
        }

# forms.py
from django import forms
from .models import SolderingBitRecord, MachineLocation

class SolderingBitRecordSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    machine_no = forms.ChoiceField(
        required=False
    )
    machine_location = forms.ChoiceField(
        choices=(('', 'All'),) + tuple(SolderingBitRecord.LOCATION_CHOICES),
        required=False
    )
    part_name = forms.ChoiceField(
        choices=(('', 'All'),) + tuple(SolderingBitRecord.PART_CHOICES),
        required=False
    )
    bit_size = forms.ChoiceField(
        choices=(('', 'All'),) + tuple(SolderingBitRecord.TICK_CHOICES),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically update machine_no choices
        machine_choices = [('', 'All')] + [(str(m.id), m.location_name) 
                                         for m in MachineLocation.objects.all()]
        self.fields['machine_no'].choices = machine_choices
        
        # ----------------------------------------------------------------


from .models import DailyChecklistItem,MonthlyChecklistItem,WeeklyChecklistItem,MACHINE_NAME_CHOICES


class DailyChecklistItemForm(forms.ModelForm):
    class Meta:
        model = DailyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
# forms.py
# forms.py
class DailyChecklistItemSearchForm(forms.Form):
    MACHINE_NAME_CHOICES = (
        ('tsc_01', 'TSC 01'),
        ('tsc_02', 'TSC 02'),
        ('tsc_04', 'TSC 04'),
        ('tsc_05', 'TSC 05'),
        ('tsc_09', 'TSC 09'),
        ('ebe_01', 'EBE 01'),
        ('csl_01', 'CSL 01'),
        ('dtr_03', 'DTR 03'),
        ('dtr_05', 'DTR 05'),
    )

    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    machine_name = forms.ChoiceField(
        choices=(('', 'All'),) + MACHINE_NAME_CHOICES,  # Convert list to tuple
        required=False
    )
    machine_location = forms.ModelChoiceField(
        queryset=MachineLocation.objects.all(),
        empty_label="All Locations",
        required=False
    )
    check_status = forms.ChoiceField(
        choices=(('', 'All'), ('✔', 'OK'), ('✘', 'Not OK')),  # Convert to tuple
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically update machine_location choices
        self.fields['machine_location'].queryset = MachineLocation.objects.all().order_by('location_name')
                        
class WeeklyChecklistItemForm (forms.ModelForm):
    class Meta:
        model = WeeklyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        # ---------------------------------------------------
        
# forms.py
class WeeklyChecklistItemSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    machine_name = forms.ChoiceField(
        choices=(('', 'All'),) + MACHINE_NAME_CHOICES,
        required=False
    )
    machine_location = forms.ModelChoiceField(
        queryset=MachineLocation.objects.all(),
        empty_label="All Locations",
        required=False
    )
    check_status = forms.ChoiceField(
        choices=(('', 'All'), ('✔', 'OK'), ('✘', 'Not OK')),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['machine_location'].queryset = MachineLocation.objects.all().order_by('location_name')
                
class MonthlyChecklistItemForm(forms.ModelForm):
    class Meta:
        model = MonthlyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
             
             
             # forms.py
class MonthlyChecklistItemSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    machine_name = forms.ChoiceField(
        choices=(('', 'All'),) + MACHINE_NAME_CHOICES,
        required=False
    )
    machine_location = forms.ModelChoiceField(
        queryset=MachineLocation.objects.all(),
        empty_label="All Locations",
        required=False
    )
    check_status = forms.ChoiceField(
        choices=(('', 'All'), ('✔', 'OK'), ('✘', 'Not OK')),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['machine_location'].queryset = MachineLocation.objects.all().order_by('location_name')
        
           
from django import forms
from .models import ControlChartReading

class ControlChartReadingForm(forms.ModelForm):
    class Meta:
        model = ControlChartReading
        fields = ['date', 'reading1', 'reading2', 'reading3', 'reading4', 'reading5', 'usl', 'lsl']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reading1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading4': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading5': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'usl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'lsl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
        }

    def clean(self):
        cleaned_data = super().clean()
        usl = cleaned_data.get('usl')
        lsl = cleaned_data.get('lsl')

        if usl and lsl and usl <= lsl:
            raise forms.ValidationError("USL must be greater than LSL")
        return cleaned_data        
        
# forms.py
from django import forms
from django.utils import timezone

class ReadingSearchForm(forms.Form):
    month = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'aria-label': 'Select Month'
            }
        ),
        label='Select Month'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique months from the database
        from .models import ControlChartReading
        months = (ControlChartReading.objects
                 .dates('date', 'month', order='DESC')
                 .distinct())
        
        month_choices = [('', 'All Months')]
        month_choices.extend(
            (month.strftime('%Y-%m'), month.strftime('%B %Y'))
            for month in months
        )
        self.fields['month'].choices = month_choices
            
#----------------------------------------------------------------
from .models import StartUpCheckSheet

class StartUpCheckSheetForm(forms.ModelForm):
    class Meta:
        model = StartUpCheckSheet
        fields = '__all__'  # Include all fields from the model
 
 
 
#  -------------------------------------------------------------------------
from .models import PChartData

from django import forms
from .models import PChartData
from django.core.validators import MinValueValidator

class PChartDataForm(forms.ModelForm):
    class Meta:
        model = PChartData
        fields = [
            'location', 
            'part_number_and_name', 
            'operation_number_and_stage_name',
            'department', 
            'month', 
            'date_control_limits_calculated',
            'average_sample_size', 
            'frequency', 
            'sample_size', 
            'nonconforming_units'
        ]
        widgets = {
            'location': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Location',
                'required': True
            }),
            'part_number_and_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Part Number and Name',
                'required': True
            }),
            'operation_number_and_stage_name': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Operation Stage',
                'required': True
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Department',
                'required': True
            }),
            'month': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'date_control_limits_calculated': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'average_sample_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Average Sample Size',
                'min': '1',
                'required': True
            }),
            'frequency': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Frequency',
                'min': '1',
                'required': True
            }),
            'sample_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Sample Size',
                'min': '1',
                'required': True
            }),
            'nonconforming_units': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Number of Nonconforming Units',
                'min': '0',
                'required': True
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        sample_size = cleaned_data.get('sample_size')
        nonconforming_units = cleaned_data.get('nonconforming_units')
        average_sample_size = cleaned_data.get('average_sample_size')
        month = cleaned_data.get('month')
        date_control_limits_calculated = cleaned_data.get('date_control_limits_calculated')

        validation_errors = {}

        if sample_size and nonconforming_units:
            if nonconforming_units > sample_size:
                validation_errors['nonconforming_units'] = "Number of nonconforming units cannot exceed sample size."

        if average_sample_size and sample_size:
            if average_sample_size > sample_size:
                validation_errors['average_sample_size'] = "Average sample size cannot be greater than sample size."

        if month and date_control_limits_calculated:
            if date_control_limits_calculated < month:
                validation_errors['date_control_limits_calculated'] = "Control limits calculation date cannot be earlier than the month date."

        if validation_errors:
            raise forms.ValidationError(validation_errors)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = {
                'required': f'Please enter {self.fields[field].label}',
                'invalid': f'Please enter a valid {self.fields[field].label}',
                'min_value': f'{self.fields[field].label} must be greater than or equal to %(limit_value)s'
            }