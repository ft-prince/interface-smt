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

#----------------------------------------------------------------
# RejectionSheetForm
from .models import RejectionSheet

class RejectionSheetForm(forms.ModelForm):
    class Meta:
        model = RejectionSheet
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


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


# ----------------------------------------------------------------


from .models import DailyChecklistItem,MonthlyChecklistItem,WeeklyChecklistItem


class DailyChecklistItemForm(forms.ModelForm):
    class Meta:
        model = DailyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
class WeeklyChecklistItemForm (forms.ModelForm):
    class Meta:
        model = WeeklyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
class MonthlyChecklistItemForm(forms.ModelForm):
    class Meta:
        model = MonthlyChecklistItem
        fields = '__all__'
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
                
from django import forms
from .models import ControlChartReading

class ControlChartReadingForm(forms.ModelForm):
    class Meta:
        model = ControlChartReading
        fields = ['date', 'reading1', 'reading2', 'reading3', 'reading4', 'reading5']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }                