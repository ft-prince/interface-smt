from django import forms
from .models import QSF, ProcessMachineMapping, Screen

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
    # qsf_document = forms.ModelChoiceField(
    #     queryset=QSF.objects.all(),
    #     label="QSF Document",
    #     empty_label="Select a QSF document"
    #  )
    # process_machine=forms.ModelChoiceField(
    #     queryset=ProcessMachineMapping.objects.all(),
    #     label="Process Machine",
    #     empty_label="Select a Process"
    # )
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
            'custom_defect': forms.TextInput(attrs={'style': 'display:none;'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize defect select as empty
        self.fields['defect'].widget = forms.Select(choices=[('', '--------')])
        self.fields['defect'].required = False
        self.fields['defect_type'].required = False
        self.fields['custom_defect'].required = False
        
        # Make the process_machine field more user-friendly
        if 'process_machine' in self.fields:
            self.fields['process_machine'].label = "Machine"
            self.fields['process_machine'].widget.attrs.update({
                'class': 'form-control',
                'onchange': 'updateDefectTypeBasedOnMachine(this);'
            })
        
        # Add class to defect_type for easier JavaScript targeting
        if 'defect_type' in self.fields:
            self.fields['defect_type'].widget.attrs.update({
                'class': 'form-control defect-type-select'
            })
        
        # Add class to defect for easier JavaScript targeting  
        if 'defect' in self.fields:
            self.fields['defect'].widget.attrs.update({
                'class': 'form-control defect-select'
            })
        
        # If instance already has data, try to populate defect choices
        if self.instance and self.instance.pk and self.instance.defect_type:
            # Get appropriate choices based on defect type
            defect_type = self.instance.defect_type
            machine_name = ""
            
            # Check if there's a process machine to get machine name
            if self.instance.process_machine:
                machine_name = self.instance.process_machine.process.lower()
            
            # Debug line (optional) - remove after testing
            # print(f"Machine name in __init__: {machine_name}")
            
            # Handle special machine cases directly
            if "adhesive application" in machine_name:
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.ADHESIVE_CHOICES)
            elif "pcba screwing" in machine_name or "heatsink" in machine_name or "heat sink" in machine_name:
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.PCB_SCREWING_CHOICES)
            # Otherwise use standard defect type choices
            elif defect_type == 'visual':
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.VISUAL_CHOICES)
            elif defect_type == 'programming':
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.PROGRAMMING_CHOICES)
            elif defect_type == 'automatic_testing':
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.AUTOMATIC_TESTING_CHOICES)
            elif defect_type == 'pcb_screwing':
                # Add this condition to explicitly handle the case when defect_type is already set
                self.fields['defect'].widget = forms.Select(choices=[('', '--------')] + RejectionSheet.PCB_SCREWING_CHOICES)
    
    def clean(self):
        cleaned_data = super().clean()
        defect_type = cleaned_data.get('defect_type')
        defect = cleaned_data.get('defect')
        custom_defect = cleaned_data.get('custom_defect')
        process_machine = cleaned_data.get('process_machine')
        total_rejection_qty = cleaned_data.get('total_rejection_qty', 0)
        
        # If defect is "Others", make sure custom_defect is provided
        if defect == 'Others' and not custom_defect:
            self.add_error('custom_defect', 'Please provide a custom defect description')
        
        # Handle special machine types with appropriate defect types
        if process_machine:
            machine_name = process_machine.process.lower()
            
            # Debug line (optional) - remove after testing
            # print(f"Machine name in clean: {machine_name}")
            
            # Set the appropriate defect type based on machine
            if 'adhesive application' in machine_name:
                cleaned_data['defect_type'] = 'adhesive'
            elif any(term in machine_name for term in ['pcba screwing', 'heatsink', 'heat sink']):
                cleaned_data['defect_type'] = 'pcb_screwing'
            elif 'programming' in machine_name or ('testing' in machine_name and not 'final' in machine_name):
                cleaned_data['defect_type'] = 'programming'
            elif 'final testing' in machine_name or 'automatic' in machine_name:
                cleaned_data['defect_type'] = 'automatic_testing'
            else:
                # Default to visual for other machines
                cleaned_data['defect_type'] = 'visual'
        
        # Only require defect and defect type if there are rejections
        if total_rejection_qty > 0:
            if not defect_type:
                self.add_error('defect_type', 'Please select a defect type for the rejections')
            if not defect:
                self.add_error('defect', 'Please select a defect for the rejections')
        
        return cleaned_data
    
class RejectionSheetSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    station = forms.ChoiceField(choices=[('', 'All')] + STATION_CHOICES, required=False)  # Use the imported STATION_CHOICES
    stage = forms.ChoiceField(choices=[('', 'All')] + RejectionSheet.STAGE_CHOICES, required=False)
    part_description = forms.ChoiceField(choices=[('', 'All')] + STATION_CHOICES, required=False)  # Assuming part_description uses STATION_CHOICES
# ----------------------------------------------------------------

from .models import SolderingBitRecord 

# Update your SolderingBitRecordForm:
class SolderingBitRecordForm(forms.ModelForm):
    class Meta:
        model = SolderingBitRecord
        fields = [
            'station', 'doc_number', 'part_name', 'machine_no', 'machine_location',
            'month', 'time', 'soldering_points_per_part', 'bit_size', 'date',
            'produce_quantity_shift_a', 'produce_quantity_shift_b', 'bit_change_date',
            'prepared_by', 'approved_by',
            'defect_type', 'defect', 'custom_defect'  # Add new fields
        ]
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'bit_change_date': forms.DateInput(attrs={'type': 'date'}),
            'defect_type': forms.Select(attrs={'class': 'form-control'}),
            'defect': forms.Select(attrs={'class': 'form-control'}),
            'custom_defect': forms.TextInput(attrs={'class': 'form-control'}),

        }
    
    # Define defect field as a ChoiceField but don't specify choices yet (will be set dynamically with JS)
    defect = forms.CharField(required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initial empty choices for defect field
        self.fields['defect'].widget.choices = [('', '---------')]

        
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
        # Define this field outside of Meta class
    # qsf_document = forms.ModelChoiceField(
    #     queryset=QSF.objects.all(),
    #     label="QSF Document",
    #     empty_label="Select a QSF document"
    # )
    # process_machine=forms.ModelChoiceField(
    #     queryset=ProcessMachineMapping.objects.all(),
    #     label="Process Machine",
    #     empty_label="Select a Process"
    # )

    class Meta:
        model = DailyChecklistItem
        exclude = ['manager']

        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'qsf_document': forms.Select(attrs={'class': 'form-select'}),
            'process_machine': forms.Select(attrs={'class': 'form-select'}),            
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
                        
# ---------------------------------------------------

class WeeklyChecklistItemForm(forms.ModelForm):
    # qsf_document = forms.ModelChoiceField(
    #     queryset=QSF.objects.all(),
    #     label="QSF Document",
    #     empty_label="Select a QSF document"
    #  )
    # process_machine=forms.ModelChoiceField(
    #     queryset=ProcessMachineMapping.objects.all(),
    #     label="Process Machine",
    #     empty_label="Select a Process"
    # )
    class Meta:
        model = WeeklyChecklistItem
        exclude = ['manager']
        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'qsf_document': forms.Select(attrs={'class': 'form-select'}),  
            'process_machine': forms.Select(attrs={'class': 'form-select'}),            

        }
               
        
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
    # qsf_document = forms.ModelChoiceField(
    #     queryset=QSF.objects.all(),
    #     label="QSF Document",
    #     empty_label="Select a QSF document"
    # )
    # process_machine=forms.ModelChoiceField(
    #     queryset=ProcessMachineMapping.objects.all(),
    #     label="Process Machine",
    #     empty_label="Select a Process"
    # )    
    class Meta:
        model = MonthlyChecklistItem
        exclude = ['manager']

        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'qsf_document': forms.Select(attrs={'class': 'form-select'}),  # Add this
            'process_machine': forms.Select(attrs={'class': 'form-select'}),            
           
        }
             
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
        
           
from .models import ControlChartReading

class ControlChartReadingForm(forms.ModelForm):
    class Meta:
        model = ControlChartReading
        fields = ['date', 'reading1', 'reading2', 'reading3', 'reading4', 'reading5', 'usl', 'lsl']
        exclude = ['time']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reading1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading4': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reading5': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'usl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'readonly': 'readonly'}),
            'lsl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make USL and LSL optional in the form
        self.fields['usl'].required = False
        self.fields['lsl'].required = False

    def clean(self):
        cleaned_data = super().clean()
        usl = cleaned_data.get('usl')
        lsl = cleaned_data.get('lsl')

        if usl and lsl and usl <= lsl:
            raise forms.ValidationError("USL must be greater than LSL")
        return cleaned_data
      
from django.core.validators import MinValueValidator, MaxValueValidator
  
class SingleReadingForm(forms.Form):
    reading_value = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.1'}),
        label="Reading Value"
    )
    usl = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'readonly': 'readonly'}),
        required=False,
        validators=[MinValueValidator(0)]
    )
    lsl = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'readonly': 'readonly'}),
        required=False,
        validators=[MinValueValidator(0)]
    )

    def clean(self):
        cleaned_data = super().clean()
        usl = cleaned_data.get('usl')
        lsl = cleaned_data.get('lsl')

        if usl and lsl and usl <= lsl:
            raise forms.ValidationError("USL must be greater than LSL")
        
        reading_value = cleaned_data.get('reading_value')
        if reading_value is not None and reading_value < 0:
            self.add_error('reading_value', "Reading cannot be negative.")
            
        return cleaned_data
            
from django.utils import timezone
import datetime

class ReadingSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label='Start Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Start date',
        })
    )
    
    end_date = forms.DateField(
        required=False,
        label='End Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'End date',
        })
    )
    
    date = forms.DateField(
        required=False,
        label='Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Select date',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial dates if not provided
        today = datetime.date.today()
        
        if not self.data.get('start_date'):
            # Default start date to first day of current month
            self.initial['start_date'] = datetime.date(today.year, today.month, 1)
            
        if not self.data.get('end_date'):
            # Default end date to today
            self.initial['end_date'] = today
            
        if not self.data.get('date'):
            # Default single date to today
            self.initial['date'] = today
            
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date should be greater than or equal to start date")
            
        return cleaned_data
            
            
#----------------------------------------------------------------
from .models import StartUpCheckSheet

class StartUpCheckSheetForm(forms.ModelForm):
    class Meta:
        model = StartUpCheckSheet
        fields = '__all__'  # Include all fields from the model
        exclude = ['process_operation']
        
 
 
 
#  -------------------------------------------------------------------------
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
        
            'date_control_limits_calculated',
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
        month = cleaned_data.get('month')
        date_control_limits_calculated = cleaned_data.get('date_control_limits_calculated')

        validation_errors = {}

        if sample_size and nonconforming_units:
            if nonconforming_units > sample_size:
                validation_errors['nonconforming_units'] = "Number of nonconforming units cannot exceed sample size."

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
            
            
            
#

# forms.py
from django import forms
from .models import PCBPanelInspectionRecord

class PCBPanelInspectionRecordForm(forms.ModelForm):
    class Meta:
        model = PCBPanelInspectionRecord
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'doc_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PCBPanelInspectionRecordSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pcb_number = forms.CharField(required=False)
    customer = forms.CharField(required=False)
    pcb_batch_code = forms.CharField(required=False)
    shift = forms.ChoiceField(
        choices=[('', 'All')] + list(PCBPanelInspectionRecord.SHIFT_CHOICES), 
        required=False
    )
    inspection_status = forms.ChoiceField(
        choices=[('', 'All'), ('OK', 'OK'), ('Not OK', 'Not OK')],
        required=False
    ) 
    
    
    
    
    
    # -----
    
from django import forms
from .models import ReworkAnalysisRecord

class ReworkAnalysisRecordForm(forms.ModelForm):
    class Meta:
        model = ReworkAnalysisRecord
        exclude = ['created_by', 'created_at', 'updated_at', 'sr_no', 'process_machine']
        widgets = {
            'problem_found_date': forms.DateInput(attrs={'type': 'date'}),
            'part_received_date': forms.DateInput(attrs={'type': 'date'}),
            'analysis_date': forms.DateInput(attrs={'type': 'date'}),
            'rework_date': forms.DateInput(attrs={'type': 'date'}),
            'rev_date': forms.DateInput(attrs={'type': 'date'}),
            'defects_details': forms.Textarea(attrs={'rows': 3}),
            'reason_for_defect': forms.Textarea(attrs={'rows': 3}),
            'rework_details': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

class ReworkAnalysisRecordSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="End Date"
    )
    part_identification = forms.CharField(
        required=False, 
        label="Part Identification"
    )
    defect_type = forms.CharField(
        required=False, 
        label="Defect Type"
    )
    part_status = forms.ChoiceField(
        choices=[('', 'All')] + list(ReworkAnalysisRecord.STATUS_CHOICES),
        required=False,
        label="Part Status"
    )
    verification_status = forms.ChoiceField(
        choices=[('', 'All')] + list(ReworkAnalysisRecord.VERIFICATION_CHOICES),
        required=False,
        label="Verification Status"
    )
    department = forms.CharField(
        required=False,
        label="Department"
    )    
    
    
    
    
#------------------------   
 
from django import forms
from .models import SolderPasteControl

class SolderPasteControlForm(forms.ModelForm):
    class Meta:
        model = SolderPasteControl
        exclude = ['created_by', 'created_at', 'updated_at', 'process_machine', 'history']
        widgets = {
            'psr_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'thawing_date': forms.DateInput(attrs={'type': 'date'}),
            'thawing_time': forms.TimeInput(attrs={'type': 'time'}),
            'mixing_date': forms.DateInput(attrs={'type': 'date'}),
            'mixing_time': forms.TimeInput(attrs={'type': 'time'}),
            'first_use_date': forms.DateInput(attrs={'type': 'date'}),
            'first_use_time': forms.TimeInput(attrs={'type': 'time'}),
            'second_use_date': forms.DateInput(attrs={'type': 'date'}),
            'second_use_time': forms.TimeInput(attrs={'type': 'time'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    # Add hidden fields for the default values
    paste_type = forms.CharField(initial="Lead Free Solder Paste", widget=forms.HiddenInput())
    paste_make = forms.CharField(initial="Heraeus", widget=forms.HiddenInput())
    part_number = forms.CharField(initial="F640SA30C5-89M30", widget=forms.HiddenInput())
    alloy = forms.CharField(initial="Sn 96.5; Ag 3; Cu 0.5", widget=forms.HiddenInput())
    mesh_type = forms.CharField(initial="Type 3 =25 -45 microns (325/=500mesh)", widget=forms.HiddenInput())
    net_weight = forms.CharField(initial="500 Gms", widget=forms.HiddenInput())
    paste_code = forms.CharField(initial="G1", widget=forms.HiddenInput())
    
class SolderPasteControlSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="End Date"
    )
    serial_number = forms.CharField(
        required=False, 
        label="Serial Number (G1-)"
    )
    lot_number = forms.CharField(
        required=False, 
        label="Lot Number"
    )
    expiry_status = forms.ChoiceField(
        choices=[('', 'All')] + list(SolderPasteControl.EXPIRY_STATUS_CHOICES),
        required=False,
        label="Expiry Status"
    ) 
    
    
    
#-------------
# forms.py
from django import forms
from .models import TipVoltageResistanceRecord, QSF, ProcessMachineMapping

class TipVoltageResistanceRecordForm(forms.ModelForm):
    class Meta:
        model = TipVoltageResistanceRecord
        fields = [
            'qsf_document', 'process_machine', 'month_year', 'soldering_station_control_no', 
            'date', 'frequency', 'tip_voltage', 'tip_resistance',
        ]
        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default QSF document
        self.fields['qsf_document'].queryset = QSF.objects.all()
        self.fields['qsf_document'].initial = QSF.objects.filter(doc_number='QSF-12-09').first()
        self.fields['qsf_document'].empty_label = "Select a QSF document"
        
        # Configure process_machine field
        self.fields['process_machine'].queryset = ProcessMachineMapping.objects.all()
        self.fields['process_machine'].empty_label = "Select a Process"
        
        # Add help text for measurements
        self.fields['tip_voltage'].help_text = "Must be less than 1V"
        self.fields['tip_resistance'].help_text = "Must be less than 10Ω"

class TipVoltageResistanceRecordSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    frequency = forms.ChoiceField(
        choices=[('', 'All')] + TipVoltageResistanceRecord.FREQ_CHOICES,
        required=False
    )
    shift = forms.ChoiceField(
        choices=[('', 'All')] + TipVoltageResistanceRecord.SHIFT_CHOICES, 
        required=False
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All'), 
            ('ok', 'OK (Within Limits)'), 
            ('not_ok', 'Not OK (Out of Limits)')
        ],
        required=False
    )
    soldering_station_control_no = forms.CharField(required=False) 