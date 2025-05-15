#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import django
from simple_history.models import HistoricalRecords

CONTROL_NUMBER_CHOICES = (
        ('51-00-4283-3', '51-00-4283-3'),
        ('51-00-2603-3', '51-00-2603-3'),
        ('51-00-1466-3', '51-00-1466-3'),
        ('57-00-2141-3', '57-00-2141-3'),
        ('57-00-1891-3', '57-00-1891-3'),
        ('56-00-1702-3', '56-00-1702-3'),
        ('56-00-2461-2', '56-00-2461-2'),
        ('56-00-1019-2', '56-00-1019-2'),
        ('56-00-1454-2', '56-00-1454-2'),
        ('56-00-1737-3', '56-00-1737-3'),
        ('56-00-2305-3', '56-00-2305-3'),
        ('51-00-2305-3', '51-00-2305-3'),
        ('51-00-3585-3', '51-00-3585-3'),
        ('51-00-2629-3', '51-00-2629-3'),
        ('57-00-1578-3', '57-00-1578-3'),
        ('57-00-1579-3', '57-00-1579-3'),
        ('51-00-3228-3', '51-00-3228-3'),
        ('56-00-2450-3', '56-00-2450-3'),
        ('52-00-1035-1', '52-00-1035-1'),
    )

class MachineLocation(models.Model):
    location_name = models.CharField(max_length=100, unique=True, verbose_name="Machine Location")
    min_skill_required = models.IntegerField(verbose_name="Minimum Skill Required")

    def __str__(self):
        return self.location_name

MACHINE_LOCATION_CHOICES = (
        ('visual_inspection', 'Visual Inspection'),
        ('programming_testing', 'Programming & Testing'),
        ('function_testing', 'Function Testing'),
        ('adhesive_application', 'Adhesive Application'),
        ('conformal_coating', 'Conformal Coating'),
        ('housing', 'Housing'),
        ('e90fl', 'E90FL'),
        ('dr_beck_epoxy', 'Dr. Beck Epoxy'),
        ('final_testing', 'Final Testing'),
        # Add more locations as needed
    )
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
        # Add more machines as needed
    )


STATION_CHOICES = [
        ('EFL01_S01', 'EFL01_S01'),
        ('EFL01_S02', 'EFL01_S02'),
        ('EFL01_S03', 'EFL01_S03'),
        ('EFL01_S04', 'EFL01_S04'),
        ('EFL01_S05', 'EFL01_S05'),
        ('EFL01_S06', 'EFL01_S06'),
        ('EFL01_S07', 'EFL01_S07'),
        ('EFL01_S08', 'EFL01_S08'),
        ('EFL01_S09', 'EFL01_S09'),
    ]


class Product(models.Model):
    name = models.CharField(max_length=100)
    status_choices = [
        ('RUNNING', 'Running'),
        ('STOPPED', 'Stopped'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='STOPPED')

    def __str__(self):
        return self.name


class Screen(models.Model):
    screen_id = models.AutoField(primary_key=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    video_path = models.CharField(max_length=100, null=True, blank=True)
    pdf_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Screen {self.screen_id} at {self.manager} for {self.product}"
    

from django.db import models

class Defects(models.Model):
    VISUAL_CHOICES = [
        ('Dry Solder', 'Dry Solder'),
        ('No Solder', 'No Solder'),
        ('Shorting/ Bridging', 'Shorting/ Bridging'),
        ('Pad Damage', 'Pad Damage'),
        ('Component Tombstone', 'Component Tombstone'),
        ('Solder Ball', 'Solder Ball'),
        ('Green Masking improper', 'Green Masking improper'),
        ('Masking Improper', 'Masking Improper'),
        ('Component Shifted', 'Component Shifted'),
        ('Pad Lifted', 'Pad Lifted'),
        ('Component Damage/Break', 'Component Damage/Break'),
        ('Solder Projection', 'Solder Projection'),
        ('Track Cut (Open)', 'Track Cut (Open)'),
        ('Wrong Polarity', 'Wrong Polarity'),
        ('PTH Shorting', 'PTH Shorting'),
        ('Component Wrong', 'Component Wrong'),
        ('Component Missing', 'Component Missing'),
        ('Solder Dust', 'Solder Dust'),
        ('Pin Hole', 'Pin Hole'),
        ('Component Up Side Down', 'Component Up Side Down'),
        ('LED Defects', 'LED Defects'),
        ('Microcontroller Pin Bend/Damage', 'Microcontroller Pin Bend/Damage'),
        ('Solder Crack', 'Solder Crack'),
        ('Others', 'Others'),
    ]

    PROGRAMMING_CHOICES = [
        ('Programme does not accept', 'Programme does not accept'),
        ('Pin Voltage low', 'Pin Voltage low'),
        ('Others', 'Others'),
    ]

    AUTOMATIC_TESTING_CHOICES = [
        ('Testing fail', 'Testing fail'),
        ('Others', 'Others'),
    ]

    visual_defect = models.CharField(max_length=100, choices=VISUAL_CHOICES, default='Others',blank=True)
    programming_defect = models.CharField(max_length=100, choices=PROGRAMMING_CHOICES, default='Others',blank=True)
    automatic_testing_defect = models.CharField(max_length=100, choices=AUTOMATIC_TESTING_CHOICES, default='Others',blank=True)

    def __str__(self):
        return f"{self.visual_defect} | {self.programming_defect} | {self.automatic_testing_defect}"



class ProcessMachineMapping(models.Model):
    station = models.CharField(max_length=100, )
    process_no = models.CharField(max_length=100,blank=True,null=True )
    process = models.CharField(max_length=100, )
    part_name=models.CharField(max_length=100,blank=True,null=True )
    machine_name = models.CharField(max_length=100, )
    control_number = models.CharField(max_length=100, )
    Usl=models.FloatField(default=0,blank=True,null=True)
    Lsl=models.FloatField(default=0,blank=True,null=True)
    
    def __str__(self):
        return f"{self.station} - {self.process} - {self.machine_name} -{self.process_no} - {self.control_number}"
    
    class Meta:
        unique_together = ('station', 'process' )
        verbose_name = "Process-Machine Mapping"
        verbose_name_plural = "Process-Machine Mappings"

# ----------------------------------------------------------------
# FixtureCleaningRecord
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# SolderingBitRecord
from django.db import models
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class QSF(models.Model):
    doc_number = models.CharField(max_length=20, default="QSF-13-06", blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.doc_number} Rev {self.rev_number}"
    
    
from datetime import date
   
from datetime import date
from django.utils import timezone
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class FixtureCleaningRecord(models.Model):
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    FIXTURE_LOCATION = [
        ('visual_inspection', 'Visual Inspection'),
        ('programming_testing', 'Programming & Testing'),
        ('function_testing', 'Function Testing'),
        ('adhesive_application', 'Adhesive Application'),
        ('conformal_coating', 'Conformal Coating'),
        ('housing', 'Housing'),
        ('e90fl', 'E90FL'),
        ('dr_beck_epoxy', 'Dr. Beck Epoxy'),
        ('final_testing', 'Final Testing'),
    ]
    
    TAG_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

    modified_TAG_CHOICES =[
        ('No Peel off','NO PEEL OFF'),
        ('No Damage','NO DAMAGE'),
        ('Not Available', 'Not Available')
    ]

    # Fields from FixtureCleaningRecord
    station = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 12-16",null=True,blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 00 ",null=True,blank=True)
    
    rev_date = models.DateField( null=True, blank=True)

    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='FixtureCleaningRecord',null=True,blank=True)
    process_machine=models.ForeignKey(ProcessMachineMapping,on_delete=models.CASCADE,related_name='FixtureCleaningRecord',null=True,blank=True)    
    month_year = models.DateField(default=timezone.now, blank=True)
    
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES,blank=True,null=True)
    
    fixture_location = models.CharField(max_length=100, null=True, blank=True)
    fixture_control_no = models.CharField(max_length=100, null=True, blank=True)
    fixture_installation_date = models.DateField(default=timezone.now, blank=True)
    # Fields from DailyRecord
    date = models.DateField(default=timezone.now,blank=True)
    time = models.TimeField(default=timezone.now,blank=True)
    
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    verification_tag_available = models.CharField(max_length=25, choices=TAG_CHOICES)
    verification_tag_condition = models.CharField(max_length=250, choices=modified_TAG_CHOICES)
    no_dust_on_fixture = models.CharField(max_length=25, choices=TAG_CHOICES)
    no_epoxy_coating_on_fixture = models.CharField(max_length=25, choices=TAG_CHOICES)
    operator_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✔',blank=True)
    supervisor_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✘',blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Fixture Cleaning Record"
        verbose_name_plural = "Fixture Cleaning Records"

    def save(self, *args, **kwargs):
        """
        Override save method to auto-populate fields based on logged-in machine,
        generate notifications for cleaning issues, and auto-determine shift based on time.
        """
        from datetime import datetime
        # Auto-determine shift based on time
        self.time = datetime.now().time()
        # Auto-determine shift based on time
        if self.time:
            # The self.time is already a time object from TimeField
            current_time = self.time
            
            # Import datetime properly
            from datetime import time as datetime_time
            
            # Define shift time ranges
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            # shift_b_end is 00:30 next day, but we'll handle overnight differently
            
            # Check if time falls within Shift A
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            # Check if time falls within Shift B (accounting for overnight)
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            # If time doesn't fit either shift, default to closest one
            else:
                # This handles gaps like 16:00-16:30
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                if abs(morning_diff) < abs(evening_diff):
                    self.shift = 'A'
                else:
                    self.shift = 'B'
        
        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
        
        # Proceed with existing functionality
        print("Before save:")
        print(f"process_machine: {self.process_machine}")
        print(f"station: {self.station}")
        print(f"machine_name: {self.fixture_location}")
        print(f"control_number: {self.fixture_control_no}")

        # Auto-populate from process_machine if available
        if self.process_machine:
            # No validation needed since we removed choices constraints
            self.station = self.process_machine.station
            self.fixture_location = self.process_machine.machine_name
            self.fixture_control_no = self.process_machine.control_number
            
            # Try to find a matching machine_location
            try:
                # First try exact match on process name
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                # If not found, try substring match
                if not location:
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                if location:
                    self.machine_location = location
            except Exception as e:
                # Just log the error and continue
                print(f"Error setting machine_location: {e}")
        
        # Handle operator assignment if available
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user

        # Call parent save method
        super().save(*args, **kwargs)
        print("After population:")
        print(f"process_machine: {self.process_machine}")
        print(f"station: {self.station}")
        print(f"machine_name: {self.fixture_location}")
        print(f"control_number: {self.fixture_control_no}")

        # Define inspection points and their corresponding issue messages
        inspection_points = {
            'verification_tag_available': 'Verification Tag not available',
            'verification_tag_condition': 'Verification Tag in poor condition',
            'no_dust_on_fixture': 'Dust detected on fixture',
            'no_epoxy_coating_on_fixture': 'Epoxy coating detected on fixture'
        }
        
        # Collect all issues found during inspection
        issues = [
            message for field, message in inspection_points.items()
            if getattr(self, field) == 'Not Available'
        ]
        
        if issues:
            self._send_notification(issues)
        
    def _send_notification(self, issues):
        """
        Send structured notification about cleaning issues.
        Includes all relevant record details and severity level.
        """
        severity = 'high' if len(issues) > 2 else 'medium'
        
        notification = {
            'type': 'chat_message',
            'message': {
                'alert_type': 'fixture_cleaning_alert',
                'record_id': self.pk,
                'fixture_number': self.fixture_control_no,
                'location': self.fixture_location,
                'date': self.date.strftime('%Y-%m-%d'),
                'shift': self.shift,
                'issues': issues,
                'severity': severity
            }
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('test', notification)

    def __str__(self):
        """String representation of the cleaning record."""
        return f"Cleaning Record {self.fixture_control_no} - {self.date}"




# ----------------------------------------------------------------
# Rejection sheet

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal




class RejectionSheet(models.Model):
    STAGE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C','C')
    ]
    DEFECT_TYPE_CHOICES = [
        ('visual', 'Visual Defects'),
        ('programming', 'Programming Defects'),
        ('automatic_testing', 'Automatic Testing Defects'),
        ('adhesive', 'Adhesive Application Defects'),  # Add this for Adhesive Application
        ('pcb_screwing', 'PCB Screwing Defects'),  # Add this for PCB Screwing with Heat Sink
    ]
    
    VISUAL_CHOICES = [
        ('Dry Solder', 'Dry Solder'),
        ('No Solder', 'No Solder'),
        ('Shorting/ Bridging', 'Shorting/ Bridging'),
        ('Pad Damage', 'Pad Damage'),
        ('Component Tombstone', 'Component Tombstone'),
        ('Solder Ball', 'Solder Ball'),
        ('Green Masking improper', 'Green Masking improper'),
        ('Masking Improper', 'Masking Improper'),
        ('Component Shifted', 'Component Shifted'),
        ('Pad Lifted', 'Pad Lifted'),
        ('Component Damage/Break', 'Component Damage/Break'),
        ('Solder Projection', 'Solder Projection'),
        ('Track Cut (Open)', 'Track Cut (Open)'),
        ('Wrong Polarity', 'Wrong Polarity'),
        ('PTH Shorting', 'PTH Shorting'),
        ('Component Wrong', 'Component Wrong'),
        ('Component Missing', 'Component Missing'),
        ('Solder Dust', 'Solder Dust'),
        ('Pin Hole', 'Pin Hole'),
        ('Component Up Side Down', 'Component Up Side Down'),
        ('LED Defects', 'LED Defects'),
        ('Microcontroller Pin Bend/Damage', 'Microcontroller Pin Bend/Damage'),
        ('Solder Crack', 'Solder Crack'),
        ('Others', 'Others'),
    ]
    
    PROGRAMMING_CHOICES = [
        ('Programme does not accept', 'Programme does not accept'),
        ('Pin Voltage low', 'Pin Voltage low'),
        ('Others', 'Others'),
    ]
    
    AUTOMATIC_TESTING_CHOICES = [
        ('Testing fail', 'Testing fail'),
        ('Others', 'Others'),
    ]
    ADHESIVE_CHOICES = [
        ('Adhesive improper', 'Adhesive improper'),
        ('Others', 'Others'),
    ]
    
    PCB_SCREWING_CHOICES = [
        ('Thermal Paste Shape not OK', 'Thermal Paste Shape not OK'),
        ('Thread NG * Heat Sink', 'Thread NG * Heat Sink'),
        ('Thread NG * Screw', 'Thread NG * Screw'),
        ('Others', 'Others'),
    ]

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]
    # Basic information
    station = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 22-01",null=True,blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 00 ",null=True,blank=True)
    
    rev_date = models.DateField(null=True, blank=True)
    
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES,blank=True,null=True)
    time = models.TimeField(default=timezone.now,blank=True)

    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='RejectionSheet',null=True,blank=True)
    process_machine=models.ForeignKey(ProcessMachineMapping,on_delete=models.CASCADE,related_name='RejectionSheet',null=True,blank=True)    
   
    stage = models.CharField(max_length=100, null=True, blank=True)
    part_description = models.CharField(max_length=100, null=True, blank=True)
    part_name = models.CharField(max_length=100, null=True, blank=True)

    
    month = models.DateField(default=timezone.now,blank=True)
    date=models.DateField(default=timezone.now,blank=True)

    # Quantity fields
    opening_balance = models.IntegerField(validators=[MinValueValidator(0)])
    receive_from_rework = models.IntegerField(validators=[MinValueValidator(0)])
    total_pass_qty = models.IntegerField(validators=[MinValueValidator(0)])
    total_rejection_qty = models.IntegerField(validators=[MinValueValidator(0)])
    closing_balance = models.IntegerField(validators=[MinValueValidator(0)])
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    defects=models.ManyToManyField(Defects, blank=True)
    
    # defects = models.TextField(blank=True)
    # Signature fields
    operator_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✔',blank=True)
    verified_by = models.CharField(max_length=1, choices=TICK_CHOICES, default='✘',blank=True)
    history = HistoricalRecords()
    defect_type = models.CharField(max_length=50, choices=DEFECT_TYPE_CHOICES, blank=True, null=True, verbose_name="Defect Type")
    defect = models.CharField(max_length=100, blank=True, null=True, verbose_name="Defect") 
    custom_defect = models.CharField(max_length=200, blank=True, null=True, verbose_name="Custom Defect")

    # # Additional fields for flexibility
    # notes = models.TextField(blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rejection Sheet"
        verbose_name_plural = "Rejection Sheets"

    def calculate_metrics(self):
        """
        Calculate all relevant metrics for the rejection sheet.
        Returns a dictionary containing calculated values.
        """
        total_input = self.opening_balance + self.receive_from_rework
        total_processed = self.total_pass_qty + self.total_rejection_qty
        rejection_rate = (self.total_rejection_qty / total_processed * 100) if total_processed > 0 else Decimal('0.00')
        
        return {
            'total_input': total_input,
            'total_processed': total_processed,
            'rejection_rate': Decimal(rejection_rate).quantize(Decimal('0.01')),
            'closing_balance': total_input - total_processed
        }

    def validate_quantities(self):
        """
        Validate all quantity-related fields.
        Raises ValidationError for any invalid values.
        """
        if self.opening_balance < 0:
            raise ValidationError({"opening_balance": "Opening balance cannot be negative"})
        
        if self.receive_from_rework < 0:
            raise ValidationError({"receive_from_rework": "Rework quantity cannot be negative"})
            
        if self.total_rejection_qty < 0:
            raise ValidationError({"total_rejection_qty": "Rejection quantity cannot be negative"})

        metrics = self.calculate_metrics()
        


    def determine_severity(self):
        """
        Determine the severity level of rejections based on business rules.
        Returns 'high' or 'medium' based on rejection thresholds.
        """
        metrics = self.calculate_metrics()
        
        # High severity if rejection rate exceeds 10%
        if metrics['rejection_rate'] > 10:
            return 'high'
        # High severity if total rejections exceed 100 units
        elif self.total_rejection_qty > 100:
            return 'high'
        # Medium severity for any other rejections
        elif self.total_rejection_qty > 0:
            return 'medium'
        # Normal severity if no rejections
        return 'normal'

    def prepare_notification(self):
        """
        Prepare structured notification data for WebSocket transmission.
        Returns a complete notification message structure.
        """
        metrics = self.calculate_metrics()
        
        return {
            'type': 'chat_message',
            'message': {
                'alert_type': 'rejection_sheet_alert',
                'record_id': self.pk,
                'station': self.station,
                'stage': self.stage,
                'part_description': self.part_description,
                'date': self.month.strftime('%Y-%m-%d'),
                'metrics': {
                    'opening_balance': self.opening_balance,
                    'receive_from_rework': self.receive_from_rework,
                    'total_pass_qty': self.total_pass_qty,
                    'total_rejection_qty': self.total_rejection_qty,
                    'closing_balance': self.closing_balance,
                    'rejection_rate': float(metrics['rejection_rate'])
                },
                'needs_attention': self.total_rejection_qty > 0,
                'severity': self.determine_severity()
            }
        }

    def send_notification(self):
        """
        Send notification through WebSocket if conditions are met.
        Only sends notifications for records with rejections.
        """
        if self.total_rejection_qty > 0:
            channel_layer = get_channel_layer()
            notification = self.prepare_notification()
            async_to_sync(channel_layer.group_send)('test', notification)

    def clean(self):
        """Perform model validation before saving."""
        super().clean()
        self.validate_quantities()

    def save(self, *args, **kwargs):
        """Override save to include validation and notification."""
        self.full_clean()
        from datetime import datetime
        # Auto-determine shift based on time
        self.time = datetime.now().time()
        
        # Auto-determine shift based on time
        if self.time:
            # The self.time is already a time object from TimeField
            current_time = self.time
            
            # Import datetime properly
            from datetime import time as datetime_time
            
            # Define shift time ranges
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            # shift_b_end is 00:30 next day, but we'll handle overnight differently
            
            # Check if time falls within Shift A
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            # Check if time falls within Shift B (accounting for overnight)
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            # If time doesn't fit either shift, default to closest one
            else:
                # This handles gaps like 16:00-16:30
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                if abs(morning_diff) < abs(evening_diff):
                    self.shift = 'A'
                else:
                    self.shift = 'B'

        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine
                    

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
        
                
        # Add these at the beginning of the save method
        print("Before save:")
        print(f"station: {self.station}")
        print(f"process_machine: {self.stage}")
        print(f"control_number: {self.part_description}")

        # Auto-populate from process_machine if available
        if self.process_machine:
            # No validation needed since we removed choices constraints
            self.station = self.process_machine.station
            self.part_description = self.process_machine.machine_name
            self.stage = self.process_machine.process
            
            # Try to find a matching machine_location
            try:
                # First try exact match on process name
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                # If not found, try substring match
                if not location:
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                if location:
                    self.machine_location = location
            except Exception as e:
                # Just log the error and continue
                print(f"Error setting machine_location: {e}")
        
        # Handle manager assignment if available
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user

        # Call parent save method
        super().save(*args, **kwargs)
        print("After population:")
        print(f"station: {self.station}")
        print(f"process_machine: {self.stage}")
        print(f"control_number: {self.part_description}")

        
        
        super().save(*args, **kwargs)
        self.send_notification()

    def __str__(self):
        """String representation of the rejection sheet."""
        return f"Rejection Sheet for {self.part_description} - {self.month.strftime('%B %Y')} ({self.stage})"

# ----------------------------------------------------------------

    
class SolderingBitRecord(models.Model):
    PART_CHOICES = (
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

    MACHINE_CHOICES = (
        ('M1', 'Machine 1'),
        ('M2', 'Machine 2'),
        ('M3', 'Machine 3'),
    )

    LOCATION_CHOICES = (
        ('visual_inspection', 'Visual Inspection'),
        ('programming_testing', 'Programming & Testing'),
        ('function_testing', 'Function Testing'),
        ('adhesive_application', 'Adhesive Application'),
        ('conformal_coating', 'Conformal Coating'),
        ('housing', 'Housing'),
        ('e90fl', 'E90FL'),
        ('dr_beck_epoxy', 'Dr. Beck Epoxy'),
        ('final_testing', 'Final Testing'),
    )

    TICK_CHOICES_Mark = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked'),
    ]
    TICK_CHOICES = [
        ('20d', '20D'),
        ('30d', '30D'),
    ]
        # New defect type choices
    DEFECT_TYPE_CHOICES = [
        ('visual', 'Visual Defects'),
        ('programming', 'Programming Defects'),
        ('automatic_testing', 'Automatic Testing Defects'),
    ]
    
    VISUAL_CHOICES = [
        ('Dry Solder', 'Dry Solder'),
        ('No Solder', 'No Solder'),
        ('Shorting/ Bridging', 'Shorting/ Bridging'),
        ('Pad Damage', 'Pad Damage'),
        ('Component Tombstone', 'Component Tombstone'),
        ('Solder Ball', 'Solder Ball'),
        ('Green Masking improper', 'Green Masking improper'),
        ('Masking Improper', 'Masking Improper'),
        ('Component Shifted', 'Component Shifted'),
        ('Pad Lifted', 'Pad Lifted'),
        ('Component Damage/Break', 'Component Damage/Break'),
        ('Solder Projection', 'Solder Projection'),
        ('Track Cut (Open)', 'Track Cut (Open)'),
        ('Wrong Polarity', 'Wrong Polarity'),
        ('PTH Shorting', 'PTH Shorting'),
        ('Component Wrong', 'Component Wrong'),
        ('Component Missing', 'Component Missing'),
        ('Solder Dust', 'Solder Dust'),
        ('Pin Hole', 'Pin Hole'),
        ('Component Up Side Down', 'Component Up Side Down'),
        ('LED Defects', 'LED Defects'),
        ('Microcontroller Pin Bend/Damage', 'Microcontroller Pin Bend/Damage'),
        ('Solder Crack', 'Solder Crack'),
        ('Others', 'Others'),
    ]
    
    PROGRAMMING_CHOICES = [
        ('Programme does not accept', 'Programme does not accept'),
        ('Pin Voltage low', 'Pin Voltage low'),
        ('Others', 'Others'),
    ]
    
    AUTOMATIC_TESTING_CHOICES = [
        ('Testing fail', 'Testing fail'),
        ('Others', 'Others'),
    ]

    # Configuration constants
    BIT_LIFE_CONFIG = {
        '20d': {'points_per_part': 10, 'initial_life': 12000, 'warning_threshold': 2000},
        '30d': {'points_per_part': 4, 'initial_life': 6000, 'warning_threshold': 1000}
    }

    station = models.CharField(max_length=100, default='DSL01_S01')
    doc_number = models.CharField(max_length=50, verbose_name="Doc. No.", default='Doc-QSF-12-15', blank=True)
    part_name = models.CharField(max_length=100, choices=PART_CHOICES)
    machine_no = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    machine_location = models.CharField(max_length=150,choices=STATION_CHOICES)
    month = models.DateField(default=timezone.now, blank=True)
    time = models.TimeField(default=timezone.now, blank=True)
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    soldering_points_per_part = models.IntegerField(default=10)
    bit_size = models.CharField(max_length=50, choices=TICK_CHOICES)
    date = models.DateField(default=timezone.now, blank=True)
    produce_quantity_shift_a = models.IntegerField(verbose_name="Produce Quantity Shift A")
    produce_quantity_shift_b = models.IntegerField(verbose_name="Produce Quantity Shift B")
    total_quantity = models.IntegerField(verbose_name="Total Quantity (Both shifts)", default=500)
    total_soldering_points = models.IntegerField(verbose_name="Total Soldering points/day", default=500)
    bit_life_remaining = models.IntegerField(verbose_name="Bit Life Remaining (Parts in Nos.)", default=500)
    bit_change_date = models.DateField(verbose_name="Bit Change Date")
    prepared_by = models.CharField(max_length=100, choices=TICK_CHOICES_Mark, blank=True)
    approved_by = models.CharField(max_length=100, choices=TICK_CHOICES_Mark, blank=True)
        # Add the new defect fields
    # Add the defect fields but with CharField instead of choices for defect
    defect_type = models.CharField(max_length=50, choices=DEFECT_TYPE_CHOICES, blank=True, null=True, verbose_name="Defect Type")
    defect = models.CharField(max_length=100, blank=True, null=True, verbose_name="Defect") 
    custom_defect = models.CharField(max_length=200, blank=True, null=True, verbose_name="Custom Defect")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Robotic Soldering Bit Replacement Record"
        verbose_name_plural = "Robotic Soldering Bit Replacement Records"
        
    def __str__(self):
        return f"Record {self.doc_number} - {self.date}"

    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Add proper null checks before validation
        if self.produce_quantity_shift_a is None:
            raise ValidationError({
                'produce_quantity_shift_a': "Shift A quantity is required"
            })
            
        if self.produce_quantity_shift_b is None:
            raise ValidationError({
                'produce_quantity_shift_b': "Shift B quantity is required"
            })
        
        # Validate non-negative values
        if self.produce_quantity_shift_a < 0:
            raise ValidationError({
                'produce_quantity_shift_a': "Shift A quantity cannot be negative"
            })
            
        if self.produce_quantity_shift_b < 0:
            raise ValidationError({
                'produce_quantity_shift_b': "Shift B quantity cannot be negative"
            })
                # Validate that if defect is "Others", a custom defect is provided
        if self.defect == 'Others' and not self.custom_defect:
            raise ValidationError({
                'custom_defect': 'Please specify the custom defect'
            })
    
            
    def calculate_bit_life(self):
        """Calculate bit life related metrics"""
        config = self.BIT_LIFE_CONFIG[self.bit_size]
        
        self.soldering_points_per_part = config['points_per_part']
        self.total_quantity = self.produce_quantity_shift_a + self.produce_quantity_shift_b
        self.total_soldering_points = self.total_quantity * self.soldering_points_per_part
        self.bit_life_remaining = config['initial_life'] - self.total_soldering_points
        
        return config['warning_threshold']

    def get_notification_message(self, warning_threshold):
        """Generate structured notification message"""
        return {
            'type': 'chat_message',
            'message': {
                'record_id': str(self.pk),
                'alert_type': 'soldering_bit_alert',
                'station': self.station,
                'machine': str(self.machine_no.id),
                'location': self.machine_location,
                'bit_size': self.bit_size,
                'current_date': timezone.now().strftime('%Y-%m-%d'),
                'bit_change_date': self.bit_change_date.strftime('%Y-%m-%d'),
                'bit_life_remaining': self.bit_life_remaining,
                'warning_threshold': warning_threshold,
                'total_soldering_points': self.total_soldering_points,
                'status': 'critical' if self.bit_life_remaining <= 0 else 'warning',
                'metrics': {
                    'total_quantity': self.total_quantity,
                    'points_per_part': self.soldering_points_per_part,
                    'shift_a_quantity': self.produce_quantity_shift_a,
                    'shift_b_quantity': self.produce_quantity_shift_b
                }
            }
        }

    def save(self, *args, **kwargs):
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user
            
        # Run validation
        self.full_clean()
        
        # Calculate bit life and get warning threshold
        warning_threshold = self.calculate_bit_life()
        
        # Save the record
        super().save(*args, **kwargs)
        
        # Send notifications if needed
        if self.bit_life_remaining <= warning_threshold:
            channel_layer = get_channel_layer()
            notification = self.get_notification_message(warning_threshold)
            async_to_sync(channel_layer.group_send)('test', notification)

# ----------------------------------------------------------------

from django.db import models
import django.utils.timezone
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import time as datetime_time

class DailyChecklistItem(models.Model):
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True)           
    station = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 13-06", null=True, blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 02 ", null=True, blank=True)
    
    rev_date = models.DateField(default=date(2022, 12, 31),null=True, blank=True)

    # Add the missing time field
    time = models.TimeField(default=timezone.now, blank=True)
    
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES, blank=True, null=True)
    


    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='daily_checklists', null=True, blank=True)
    process_machine = models.ForeignKey(ProcessMachineMapping, on_delete=models.CASCADE, related_name='daily_process_machine', null=True, blank=True)
    machine_name = models.CharField(max_length=100, null=True, blank=True)
    control_number = models.CharField(max_length=100, null=True, blank=True)  
    part_name = models.CharField(max_length=100, null=True, blank=True)  
    process_no = models.CharField(max_length=100, null=True, blank=True)  
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation", null=True, blank=True)
    month_year = models.DateField(default=timezone.now, blank=True)
    date = models.DateField(default=django.utils.timezone.now, blank=True)
    # Main Item filled by Operator 
    CHECK_POINT_CHOICES = (
        ('Clean Machine Surface', 'Clean Machine Surface'),
        ('Check ON/OFF Switch', 'Check ON/OFF Switch'),
        ('Check Emergency Switch', 'Check Emergency Switch'),
        ('Check any Abnormal Sound in M/C', 'Check any Abnormal Sound in M/C'),
        ('Check Spray Nozzle', 'Check Spray Nozzle'),
        ('Check all Tubbing & Feeder pipe', 'Check all Tubbing & Feeder pipe'),
        ('Check Maintenance & Calibration Tag', 'Check Maintenance & Calibration Tag'),
    )
    
    
    METHOD_OF_CHECKING_CHOICES = (
        ('Clean by Cloths & Brush', 'Clean by Cloths & Brush'),
        ('By Hand', 'By Hand'),
        ('By Eye', 'By Eye'),
    )     
 
    Remark_1 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_2 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_3 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_4 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_5 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_6 = models.CharField(max_length=100, choices=TICK_CHOICES)   
    Remark_7 = models.CharField(max_length=100, choices=TICK_CHOICES)   
     
   
    
    checked_by_Operator = models.CharField(max_length=100, choices=TICK_CHOICES, default='✔', blank=True)
    approved_by_Supervisor = models.CharField(max_length=100, choices=TICK_CHOICES, default='✘', blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Maintenance Checklist For Daily"
        verbose_name_plural = "Maintenance Checklists For Daily"

    def __str__(self):
        return f"Daily Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def get_notification_message(self, checkpoint_number, status):
        """
        Generate a notification message with hardcoded checkpoint details.
        """
        # Define hardcoded checkpoint values
        checkpoints = [
            'Clean Machine Surface',
            'Check ON/OFF Switch',
            'Check Emergency Switch',
            'Check any Abnormal Sound in M/C',
            'Check Spray Nozzle',
            'Check all Tubbing & Feeder pipe',
            'Check Maintenance & Calibration Tag'
        ]
        
        requirements = [
            'Proper Clean',
            'Proper Working',
            'Proper Working',
            'No any Abnormal Sound',
            'No Blockage No leakage',
            'No Cut & No Damage',
            'No Expiry date on tag'
        ]
        
        methods = [
            'Clean by Cloths & Brush',
            'By Hand',
            'By Hand',
            'By Eye',
            'By Eye',
            'By Eye',
            'By Eye'
        ]
        
        # Adjust index for 0-based list
        idx = checkpoint_number - 1
        
        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'alert_type': 'daily_checklist_alert',
                # Core machine information
                'machine_name': self.machine_name or 'N/A',
                'machine_location': str(self.machine_location) or 'N/A',
                'station': self.station or 'N/A',
                'control_number': self.control_number or None,
                'date': self.date.strftime('%Y-%m-%d'),

                # Checkpoint details structured to match frontend expectations
                'checkpoint': {
                    'number': checkpoint_number,
                    'name': checkpoints[idx] if idx < len(checkpoints) else 'N/A',
                    'requirement': requirements[idx] if idx < len(requirements) else 'N/A',
                    'method': methods[idx] if idx < len(methods) else 'N/A',
                    'status': '✘'  # Status symbol for failed checkpoint
                },
                
                # Additional metadata for alert handling
                'needs_attention': True,
                'severity': 'high' if status == '✘' else 'normal',
                'check_frequency': 'daily'  # Added to match frontend formatting
            }
        }

    def save(self, *args, **kwargs):
        """
        Save the checklist and generate notifications for failed checkpoints.
        """
        from datetime import datetime
        # Auto-determine shift based on time
        self.time = datetime.now().time()
        
        # Auto-determine shift based on time
        if hasattr(self, 'time') and self.time:
            # The self.time is already a time object from TimeField
            current_time = self.time
            
            # Define shift time ranges
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            # shift_b_end is 00:30 next day, but we'll handle overnight differently
            
            # Check if time falls within Shift A
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            # Check if time falls within Shift B (accounting for overnight)
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            # If time doesn't fit either shift, default to closest one
            else:
                # This handles gaps like 16:00-16:30
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                if abs(morning_diff) < abs(evening_diff):
                    self.shift = 'A'
                else:
                    self.shift = 'B'
        

        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine
                    

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine

        # Add these at the beginning of the save method
        print("Before save:")
        print(f"process_machine: {self.process_machine}")
        print(f"station: {self.station}")
        print(f"machine_name: {self.machine_name}")
        print(f"control_number: {self.control_number}")

        # Auto-populate from process_machine if available
        if self.process_machine:
            # No validation needed since we removed choices constraints
            self.station = self.process_machine.station
            self.machine_name = self.process_machine.machine_name
            self.control_number = self.process_machine.control_number
            self.process_no = self.process_machine.process_no
            
            # Try to find a matching machine_location
            try:
                # First try exact match on process name
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                # If not found, try substring match
                if not location:
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                if location:
                    self.machine_location = location
            except Exception as e:
                # Just log the error and continue
                print(f"Error setting machine_location: {e}")
        
        # Handle manager assignment if available
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        # Call parent save method
        super().save(*args, **kwargs)
        print("After population:")
        print(f"station: {self.station}")
        print(f"machine_name: {self.machine_name}")
        print(f"control_number: {self.control_number}")
        print(f"control_number: {self.process_no}")

        # Send notifications for failed checkpoints
        channel_layer = get_channel_layer()
        
        for i in range(1, 8):  # Assuming 7 checkpoints
            remark = getattr(self, f'Remark_{i}')
            if remark == '✘':  # Check for failed status
                notification = self.get_notification_message(i, remark)
                async_to_sync(channel_layer.group_send)('test', notification)                
 
                
class WeeklyChecklistItem(models.Model):
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None ,blank=True)       
    station = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 13-06", null=True, blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 02 ", null=True, blank=True)
    part_name = models.CharField(max_length=60 , null=True, blank=True)
    
    rev_date = models.DateField(default=date(2022, 12, 31),null=True, blank=True)

    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES,blank=True,null=True)
    
    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='weekly_checklists',null=True,blank=True)
    process_machine=models.ForeignKey(ProcessMachineMapping,on_delete=models.CASCADE,related_name='weekly_process_machine',null=True,blank=True)
    
    machine_name = models.CharField(max_length=100, null=True, blank=True)
    control_number = models.CharField(max_length=100, null=True, blank=True)  
    process_no = models.CharField(max_length=100, null=True, blank=True)  
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation",null=True,blank=True)

    month_year = models.DateField(default=timezone.now,blank=True)
    date=models.DateField(default=django.utils.timezone.now,blank=True,null=True)
        

    # Weekly Checklist field
    # Choices for check points
    CHECK_POINT_CHOICES = (
        ('Check Conveyor Belts', 'Check Conveyor Belts'),
        ('Check Solder bit Assembly. For any Bolts & Screw Loose', 'Check Solder bit Assembly. For any Bolts & Screw Loose'),
        ('Check Wire & Cable', 'Check Wire & Cable'),
        ('Electrical Insulation', 'Electrical Insulation'),
    )
    date = models.DateField(default=timezone.now,blank=True)

    Remark_8=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_9=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_10=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_11=models.CharField(max_length=100,choices=TICK_CHOICES)   
    
    checked_by_Operator = models.CharField(max_length=100,choices=TICK_CHOICES,default='✔',blank=True)
    approved_by_Supervisor = models.CharField(max_length=100,choices=TICK_CHOICES,default='✘',blank=True)
    history = HistoricalRecords()

    
    
    CHECKPOINTS = {
        8: {'name': 'Check Conveyor Belts', 'requirement': 'No Damage', 'method': 'By Hand'},
        9: {'name': 'Check Solder bit Assembly. For any Bolts & Screw Loose', 'requirement': 'Proper Tight', 'method': 'By Hand'},
        10: {'name': 'Check Wire & Cable', 'requirement': 'No Damage No Broken', 'method': 'By Hand'},
        11: {'name': 'Electrical Insulation', 'requirement': 'No Cut & No Damage Wire', 'method': 'By Hand'}
    }

    class Meta:
        verbose_name = "Maintenance Checklist For Weekly"
        verbose_name_plural = "Maintenance Checklists For Weekly"

    def __str__(self):
        return f"Weekly Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def get_checkpoint_info(self, checkpoint_number):
        """
        Retrieve checkpoint information from CHECKPOINTS dictionary.
        Ensures consistent checkpoint data access.
        """
        checkpoint = self.CHECKPOINTS.get(checkpoint_number, {})
        return {
            'number': checkpoint_number,
            'name': checkpoint.get('name', getattr(self, f'check_point_{checkpoint_number}', 'N/A')),
            'requirement': checkpoint.get('requirement', getattr(self, f'requirement_range_{checkpoint_number}', 'N/A')),
            'method': checkpoint.get('method', getattr(self, f'method_of_checking_{checkpoint_number}', 'N/A')),
        }

    def get_notification_message(self, checkpoint_number, status):
        """
        Generate structured notification message for weekly checklist.
        Matches the frontend formatting requirements.
        """
        checkpoint_info = self.get_checkpoint_info(checkpoint_number)
        
        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'alert_type': 'weekly_checklist_alert',
                # Machine details
                'machine_name': self.machine_name or 'N/A',
                'machine_location': str(self.machine_location) or 'N/A',
                'station': self.station or 'N/A',
                'control_number': self.control_number or None,
                'date': self.date.strftime('%Y-%m-%d'),
                
                # Checkpoint details
                'checkpoint': {
                    'number': checkpoint_info['number'],
                    'name': checkpoint_info['name'],
                    'requirement': checkpoint_info['requirement'],
                    'method': checkpoint_info['method'],
                    'status': '✘'
                },
                
                # Alert metadata
                'needs_attention': True,
                'severity': 'high' if status == '✘' else 'normal',
                'check_frequency': 'weekly'
            }
        }

    def save(self, *args, **kwargs):
        """
        Save checklist and generate notifications for failed checkpoints.
        Handles manager assignment and notification dispatch.
        """
        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        from datetime import datetime
        # Auto-determine shift based on time
        self.time = datetime.now().time()
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine
                    

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
        
        # Auto-populate from process_machine if available
        if self.process_machine:
            # No validation needed since we removed choices constraints
            self.station = self.process_machine.station
            self.machine_name = self.process_machine.machine_name
            self.control_number = self.process_machine.control_number
            self.process_no=self.process_machine.process_no
            
            # Try to find a matching machine_location
            try:
                # First try exact match on process name
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                # If not found, try substring match
                if not location:
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                if location:
                    self.machine_location = location
            except Exception as e:
                # Just log the error and continue
                print(f"Error setting machine_location: {e}")
        
        # Handle manager assignment if available
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        # Call parent save method
        super().save(*args, **kwargs)
        print("After population:")
        print(f"station: {self.station}")
        print(f"machine_name: {self.machine_name}")
        print(f"control_number: {self.control_number}")
        print(f"control_number: {self.process_no}")

        # Send notifications for failed checkpoints
        channel_layer = get_channel_layer()

        
        # Weekly checklist uses checkpoints 8-11
        for checkpoint_number in range(8, 12):
            remark = getattr(self, f'Remark_{checkpoint_number}')
            if remark == '✘':
                notification = self.get_notification_message(checkpoint_number, remark)
                async_to_sync(channel_layer.group_send)('test', notification)

    
from django.db import models
import django.utils.timezone
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import time as datetime_time

class MonthlyChecklistItem(models.Model):
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]        
    
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True) 
    station = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 13-06", null=True, blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 02 ", null=True, blank=True)
    
    rev_date = models.DateField(default=date(2022, 12, 31),null=True, blank=True)


    # Add the missing time field
    time = models.TimeField(default=timezone.now, blank=True)
    
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES, blank=True, null=True)
    
    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='monthly_checklists', null=True, blank=True)
    
    process_machine = models.ForeignKey(ProcessMachineMapping, on_delete=models.CASCADE, related_name='monthly_process_machine', null=True, blank=True)
    machine_name = models.CharField(max_length=100, null=True, blank=True)
    control_number = models.CharField(max_length=100, null=True, blank=True)  
    part_name = models.CharField(max_length=100, null=True, blank=True)  
    process_no = models.CharField(max_length=100, null=True, blank=True)  
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation", null=True, blank=True)

    month_year = models.DateField(default=timezone.now, blank=True)
    date = models.DateField(default=django.utils.timezone.now, blank=True, null=True)

    CHECK_POINT_CHOICES = (
        ('Check Machine Earthing (Leakage Voltage)', 'Check Machine Earthing (Leakage Voltage)'),        
        ('Check all parameter', 'Check all parameter'),
        ('Check Working condition', 'Check Working condition'),
        ('Check Operation of Sensors', 'Check Operation of Sensors'),
        ('Check condition of all fixture', 'Check condition of all fixture'),
    )
    # Choices for requirement ranges
    REQUIREMENT_RANGE_CHOICES = (
        ('< 2 V', '< 2 V'),
        ('Condition Proper', 'Condition Proper'),
        ('Condition Proper', 'Condition Proper'),
        ('Proper Condition', 'Proper Condition'),
    )
    METHOD_OF_CHECKING_CHOICES = (
        ('By Parameter', 'By Parameter'),
        ('By Condition', 'By Condition'),
        ('By Condition', 'By Condition'),
        ('By Fixture', 'By Fixture'),
    )
    
    Remark_12 = models.CharField(max_length=100, choices=TICK_CHOICES)
    checked_by_Operator = models.CharField(max_length=100, choices=TICK_CHOICES, default='✔', blank=True)
    approved_by_Supervisor = models.CharField(max_length=100, choices=TICK_CHOICES, default='', blank=True)
    history = HistoricalRecords()
    
    
    class Meta:
        verbose_name = "Maintenance Checklist For Monthly"
        verbose_name_plural = "Maintenance Checklists For Monthly"

    def __str__(self):
        return f"Monthly Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def get_checkpoint_details(self, checkpoint_number):
        """
        Retrieve comprehensive checkpoint details with hardcoded values.
        Returns formatted checkpoint information.
        """
        # Hardcoded checkpoint details for checkpoint 12
        if checkpoint_number == 12:
            return {
                'number': checkpoint_number,
                'name': 'Check Machine Earthing (Leakage Voltage)',
                'requirement': '< 2 V',
                'method': 'By Parameter'
            }
        else:
            return {
                'number': checkpoint_number,
                'name': 'N/A',
                'requirement': 'N/A',
                'method': 'N/A'
            }
            
    def get_machine_details(self):
        """
        Retrieve machine-related information.
        Returns formatted machine details with appropriate fallback values.
        """
        return {
            'machine_name': self.machine_name or 'N/A',
            'machine_location': str(self.machine_location) or 'N/A',
            'station': self.station or 'N/A',
            'control_number': self.control_number or None
        }

    def get_notification_message(self, checkpoint_number, status):
        """
        Generate structured notification message for monthly checklist.
        Includes comprehensive machine, checkpoint, and management information.
        """
        machine_info = self.get_machine_details()
        checkpoint_info = self.get_checkpoint_details(checkpoint_number)

        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'alert_type': 'monthly_checklist_alert',
                
                # Machine information
                'machine_name': machine_info['machine_name'],
                'machine_location': machine_info['machine_location'],
                'station': machine_info['station'],
                'control_number': machine_info['control_number'],
                'date': self.date.strftime('%Y-%m-%d'),
                
                # Checkpoint details
                'checkpoint': {
                    'number': checkpoint_info['number'],
                    'name': checkpoint_info['name'],
                    'requirement': checkpoint_info['requirement'],
                    'method': checkpoint_info['method'],
                    'status': '✘'
                },
                
                # Alert metadata
                'needs_attention': True,
                'severity': 'high' if status == '✘' else 'normal',
                'check_frequency': 'monthly',
                'manager': str(self.manager) if self.manager else 'Not Assigned'
            }
        }

    def save(self, *args, **kwargs):
        """
        Save checklist and generate notifications for failed checkpoints.
        Handles manager assignment and notification dispatch for checkpoint 12.
        """
        from datetime import datetime
        # Auto-determine shift based on time
        self.time = datetime.now().time()
        if hasattr(self, 'time') and self.time:
            # The self.time is already a time object from TimeField
            current_time = self.time
            
            # Define shift time ranges
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            # shift_b_end is 00:30 next day, but we'll handle overnight differently
            
            # Check if time falls within Shift A
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            # Check if time falls within Shift B (accounting for overnight)
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            # If time doesn't fit either shift, default to closest one
            else:
                # This handles gaps like 16:00-16:30
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                if abs(morning_diff) < abs(evening_diff):
                    self.shift = 'A'
                else:
                    self.shift = 'B'

        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine
                    
                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine

        # Auto-populate from process_machine if available
        if self.process_machine:
            # No validation needed since we removed choices constraints
            self.station = self.process_machine.station
            self.machine_name = self.process_machine.machine_name
            self.control_number = self.process_machine.control_number
            self.process_no = self.process_machine.process_no
            
            # Try to find a matching machine_location
            try:
                # First try exact match on process name
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                # If not found, try substring match
                if not location:
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                if location:
                    self.machine_location = location
            except Exception as e:
                # Just log the error and continue
                print(f"Error setting machine_location: {e}")
        
        # Handle manager assignment if available
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        # Call parent save method
        super().save(*args, **kwargs)
        print("After population:")
        print(f"station: {self.station}")
        print(f"machine_name: {self.machine_name}")
        print(f"control_number: {self.control_number}")
        print(f"control_number: {self.process_no}")

        # Send notifications for failed checkpoints
        channel_layer = get_channel_layer()
        
        if self.Remark_12 == '✘':
            notification = self.get_notification_message(12, self.Remark_12)
            async_to_sync(channel_layer.group_send)('test', notification)




# ----------------------------------------------------------------

from django.db import models
from django.db.models import Avg, StdDev
import math

from django.db import models, IntegrityError
from datetime import datetime, timedelta  # Correct import statement
from machineapp.models import Machine
class ControlChartReading(models.Model):
    # Use machine_id as the screen identifier
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='control_chart_readings', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)

    process_machine = models.ForeignKey(
        ProcessMachineMapping, 
        on_delete=models.SET_NULL,  # If mapping is deleted, keep the reading
        related_name='control_chart_readings', 
        null=True, 
        blank=True
    )

    reading1 = models.FloatField()
    reading2 = models.FloatField(null=True, blank=True)
    reading3 = models.FloatField(null=True, blank=True)
    reading4 = models.FloatField(null=True, blank=True)
    reading5 = models.FloatField(null=True, blank=True)
    usl = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    lsl = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    history = HistoricalRecords()
    last_notification_time = models.DateTimeField(null=True, blank=True)
    remaining_entries = models.IntegerField(default=5)
    
    
    class Meta:
        # Update uniqueness constraint to use machine instead of screen_id
        unique_together = [  'time']
        
    def update_notification_status(self):
        now = timezone.now()
        if not self.last_notification_time or (now - self.last_notification_time) >= timedelta(hours=1):
            self.last_notification_time = now
            if self.remaining_entries > 0:
                self.remaining_entries -= 1
            self.save(update_fields=['last_notification_time', 'remaining_entries'])

    @classmethod
    def can_add_new_reading(cls, machine, user=None):
        """Check if 90 minutes have passed since the last reading for specific machine"""
        # Admin users can bypass the time restriction if needed
        if user and (user.is_staff or user.is_superuser):
            return True
            
        today = timezone.localdate()
        today_reading = cls.objects.filter(machine=machine, date=today).first()
        
        if not today_reading:
            return True  # No readings today, so can add first reading
            
        # Get the index of the next reading to be filled (1-5)
        next_index = today_reading.get_next_reading_index()
        
        # If all readings are filled or no next index, can't add more
        if not next_index:
            return False
            
        # If this is the first reading of the day, allow it
        if next_index == 1:
            return True
        
        # For readings 2-5, check if 90 minutes have passed since the previous reading
        # The challenge here is finding when the previous reading was added
        
        # Use the historical records to find when the previous reading was added
        previous_index = next_index - 1
        
        # Map reading index to field name
        field_mapping = {
            1: 'reading1',
            2: 'reading2',
            3: 'reading3',
            4: 'reading4',
            5: 'reading5',
        }
        
        # Determine which field was last filled
        last_field = field_mapping[previous_index]
        
        # Find the most recent historical record where this field was updated
        # We can use the history to find when the field was last changed from null to a value
        history_entries = today_reading.history.order_by('-history_date')
        
        # Find when the previous reading was added (when it changed from null to a value)
        last_update_time = None
        found_change = False
        
        for i in range(len(history_entries) - 1):
            current = history_entries[i]
            previous = history_entries[i + 1]
            
            # Check if this field changed from null to a value
            current_value = getattr(current, last_field)
            previous_value = getattr(previous, last_field)
            
            if current_value is not None and previous_value is None:
                last_update_time = current.history_date
                found_change = True
                break
        
        # If we didn't find it in history, use the record's time field as fallback
        if not found_change:
            # Default to the record's time field
            latest_datetime = datetime.combine(today_reading.date, today_reading.time)
            latest_datetime = timezone.make_aware(latest_datetime)
            last_update_time = latest_datetime
        
        # Check if 90 minutes have passed
        time_since_last = timezone.now() - last_update_time
        minutes_passed = time_since_last.total_seconds() / 60
        
        return minutes_passed >= 90

    @classmethod
    def get_next_reading_time(cls, machine, user=None):
        """Get the timestamp when next reading can be added for specific machine"""
        # Admin users bypass the restriction
        if user and (user.is_staff or user.is_superuser):
            return timezone.now()
            
        today = timezone.localdate()
        today_reading = cls.objects.filter(machine=machine, date=today).first()
        
        if not today_reading:
            return timezone.now()  # No readings today, can add immediately
            
        # Get the index of the next reading to be filled (1-5)
        next_index = today_reading.get_next_reading_index()
        
        # If all readings are filled or no next index, use default
        if not next_index:
            return timezone.now() + timedelta(minutes=90)  # Default value
        
        # If this is the first reading of the day, allow it immediately
        if next_index == 1:
            return timezone.now()
        
        # For readings 2-5, calculate when 90 minutes will have passed since previous reading
        previous_index = next_index - 1
        
        # Map reading index to field name
        field_mapping = {
            1: 'reading1',
            2: 'reading2',
            3: 'reading3',
            4: 'reading4',
            5: 'reading5',
        }
        
        # Determine which field was last filled
        last_field = field_mapping[previous_index]
        
        # Find the most recent historical record where this field was updated
        history_entries = today_reading.history.order_by('-history_date')
        
        # Find when the previous reading was added (when it changed from null to a value)
        last_update_time = None
        found_change = False
        
        for i in range(len(history_entries) - 1):
            current = history_entries[i]
            previous = history_entries[i + 1]
            
            # Check if this field changed from null to a value
            current_value = getattr(current, last_field)
            previous_value = getattr(previous, last_field)
            
            if current_value is not None and previous_value is None:
                last_update_time = current.history_date
                found_change = True
                break
        
        # If we didn't find it in history, use the record's time field as fallback
        if not found_change:
            # Default to the record's time field
            latest_datetime = datetime.combine(today_reading.date, today_reading.time)
            latest_datetime = timezone.make_aware(latest_datetime)
            last_update_time = latest_datetime
        
        # Next reading time is 90 minutes after the previous one
        return last_update_time + timedelta(minutes=90)    
    @classmethod
    def get_todays_reading(cls, machine):
        """Get today's reading record for specific machine or None"""
        today = timezone.localdate()
        return cls.objects.filter(machine=machine, date=today).first()

    def get_readings(self):
        """Get all readings as a list, replacing None with 0"""
        readings = [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
        return [r if r is not None else 0 for r in readings]
        
    def get_non_null_readings(self):
        """Get only the readings that are not null"""
        readings = [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
        return [r for r in readings if r is not None]
        
    def get_next_reading_index(self):
        """Get index (1-5) of the next reading to be filled"""
        if self.reading1 is None:
            return 1
        elif self.reading2 is None:
            return 2
        elif self.reading3 is None:
            return 3
        elif self.reading4 is None:
            return 4
        elif self.reading5 is None:
            return 5
        else:
            return None  # All readings are filled

    def check_violations(self, x_bar, r):
        """Check for control chart violations"""
        violations = []
        readings = self.get_non_null_readings()
        
        # Check specification limits
        for i, reading in enumerate(readings, 1):
            if reading > self.usl:
                violations.append(f"Reading {i} ({reading:.2f}) exceeds USL ({self.usl})")
            if reading < self.lsl:
                violations.append(f"Reading {i} ({reading:.2f}) below LSL ({self.lsl})")

        # Only perform control limit checks if we have enough readings
        if len(readings) >= 2:
            # Get control limits from statistics
            control_limits = ControlChartStatistics.calculate_control_limits(machine=self.machine)
            
            # Check X-bar limits
            if x_bar > control_limits['ucl_x_bar']:
                violations.append(f"X-bar ({x_bar:.2f}) exceeds UCL ({control_limits['ucl_x_bar']:.2f})")
            if x_bar < control_limits['lcl_x_bar']:
                violations.append(f"X-bar ({x_bar:.2f}) below LCL ({control_limits['lcl_x_bar']:.2f})")
                
            # Check Range limits
            if r > control_limits['ucl_r']:
                violations.append(f"Range ({r:.2f}) exceeds UCL-R ({control_limits['ucl_r']:.2f})")
                
        return violations

    def get_notification_message(self, x_bar, r, violations):
        """Generate structured notification message"""
        capability = ControlChartStatistics.calculate_capability_indices(machine=self.machine)
        control_limits = ControlChartStatistics.calculate_control_limits(machine=self.machine)
        
        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'machine_id': self.machine.id,
                'machine_name': self.machine.name,
                'alert_type': 'control_chart_alert',
                'date': self.date.strftime('%Y-%m-%d'),
                'readings': {
                    'values': self.get_non_null_readings(),
                    'x_bar': round(x_bar, 3),
                    'range': round(r, 3)
                },
                'specification_limits': {
                    'usl': self.usl,
                    'lsl': self.lsl
                },
                'control_limits': {
                    'x_bar_ucl': round(control_limits['ucl_x_bar'], 3),
                    'x_bar_lcl': round(control_limits['lcl_x_bar'], 3),
                    'r_ucl': round(control_limits['ucl_r'], 3),
                    'r_lcl': round(control_limits['lcl_r'], 3)
                },
                'capability': {
                    'cp': round(capability['cp'], 3),
                    'cpk': round(capability['cpk'], 3),
                    'std_dev': round(capability['std_dev'], 3)
                },
                'violations': violations,
                'needs_attention': bool(violations),
                'severity': 'high' if len(violations) > 1 else 'medium' if violations else 'low'
            }
        }

    def clean(self):
        readings = self.get_non_null_readings()
        if any(reading < 0 for reading in readings):
            raise ValidationError("Readings cannot be negative.")
        if self.usl <= self.lsl:
            raise ValidationError("Upper specification limit must be greater than lower specification limit.")

    def _create_or_update_statistics(self):
        readings = self.get_non_null_readings()
        if not readings:
            return
            
        x_bar = round(sum(readings) / len(readings), 2)
        r = round(max(readings) - min(readings), 2) if len(readings) > 1 else 0

        try:
            stats = ControlChartStatistics.objects.filter(
                date=self.date,
                machine=self.machine  # Use machine instead of screen_id
            ).first()
            
            if stats:
                stats.x_bar = x_bar
                stats.r = r
                stats.usl = self.usl
                stats.lsl = self.lsl
                stats.save()
            else:
                ControlChartStatistics.objects.create(
                    date=self.date,
                    machine=self.machine,  # Use machine instead of screen_id
                    x_bar=x_bar,
                    r=r,
                    usl=self.usl,
                    lsl=self.lsl
                )
        except Exception as e:
            print(f"Error creating/updating statistics: {e}")
            raise

    def save(self, *args, **kwargs):
        try:
            

            # Check if this is a new record (not yet saved)
            is_new = self.pk is None
            
            # Get the current request from thread local if available
            request = getattr(self, 'request', None)
            
            # If we have a request and a machine isn't already set
            if request and (is_new or not self.machine):
                # Get browser key from session if logged into a machine
                browser_key = request.session.get('browser_key')
                
                if browser_key:
                    # Try to find the active machine for this browser
                    from machineapp.models import MachineLoginTracker
                    active_login = MachineLoginTracker.objects.filter(
                        browser_key=browser_key,
                        is_active=True
                    ).order_by('-created_at').first()
                    
                    if active_login:
                        # Set the machine from the active login
                        self.machine = active_login.machine
                        
                        # Try to find the ProcessMachineMapping for this machine
                        process_machine = ProcessMachineMapping.objects.filter(
                            machine_name=self.machine.name
                        ).first()
                        
                        # Set the process_machine relationship
                        if process_machine:
                            self.process_machine = process_machine
                            
                            # Update the USL and LSL values
                            if process_machine.Usl is not None:
                                self.usl = process_machine.Usl
                            if process_machine.Lsl is not None:
                                self.lsl = process_machine.Lsl
            
            # Perform validation
            self.clean()
            
            # Save the model
            super().save(*args, **kwargs)
            
            # Update statistics
            self._create_or_update_statistics()
            
        except Exception as e:
            print(f"Error saving reading or statistics: {e}")
            raise
        
# models.py
from django.db import models
from django.db.models import Avg, StdDev, Count
from django.db.models.functions import TruncMonth
import calendar

# models.py

class ControlChartStatistics(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='control_chart_statistics', null=True, blank=True)
    date = models.DateField()
    x_bar = models.FloatField()
    r = models.FloatField()
    usl = models.FloatField(default=375)
    lsl = models.FloatField(default=355)
    history = HistoricalRecords()
    


    @classmethod
    def get_monthly_statistics(cls, machine=None):
        """
        Get monthly statistics, optionally filtered by machine
        """
        try:
            query = cls.objects
            
            # If machine is provided, filter by it
            if machine:
                query = query.filter(machine=machine)
                
            monthly_stats = query.annotate(
                month=TruncMonth('date')
            ).values('month', 'machine').annotate(
                days_count=Count('id'),
                monthly_x_bar=Avg('x_bar'),
                monthly_r=Avg('r'),
                monthly_std_dev=StdDev('x_bar')
            ).order_by('-month', 'machine')

            processed_stats = []
            for stat in monthly_stats:
                if stat['month']:
                    # Get total calendar days in the month
                    total_days = calendar.monthrange(
                        stat['month'].year,
                        stat['month'].month
                    )[1]
                    
                    # Get machine name
                    machine_obj = Machine.objects.get(id=stat['machine'])
                    
                    monthly_data = {
                        'month': stat['month'],
                        'machine_id': stat['machine'],
                        'machine_name': machine_obj.name,
                        'days_count': stat['days_count'],
                        'completion_percentage': (stat['days_count'] / total_days) * 100,
                        'monthly_x_bar': stat['monthly_x_bar'] or 0,
                        'monthly_r': stat['monthly_r'] or 0,
                        'monthly_std_dev': stat['monthly_std_dev'] or 0
                    }

                    if stat['monthly_r']:
                        monthly_data.update({
                            'monthly_ucl_x_bar': stat['monthly_x_bar'] + 0.58 * stat['monthly_r'],
                            'monthly_lcl_x_bar': stat['monthly_x_bar'] - 0.58 * stat['monthly_r'],
                            'monthly_ucl_r': 2.11 * stat['monthly_r'],
                            'monthly_lcl_r': 0
                        })
                    else:
                        monthly_data.update({
                            'monthly_ucl_x_bar': 0,
                            'monthly_lcl_x_bar': 0,
                            'monthly_ucl_r': 0,
                            'monthly_lcl_r': 0
                        })

                    processed_stats.append(monthly_data)

            return processed_stats

        except Exception as e:
            print(f"Error calculating monthly statistics: {e}")
            return []
    
    
    @classmethod
    def calculate_control_limits(cls, machine=None):
        """
        Calculate control limits, optionally for a specific machine
        """
        query = cls.objects
        
        # If machine is provided, filter by it
        if machine:
            query = query.filter(machine=machine)
            
        data = query.all()
        
        if not data.exists():
            return {
                'x_bar_avg': 0,
                'r_bar': 0,
                'ucl_x_bar': 0,
                'lcl_x_bar': 0,
                'ucl_r': 0,
                'lcl_r': 0
            }

        # Calculate x_bar and range averages with rounding
        x_bars = [round(record.x_bar, 2) for record in data]
        ranges = [round(record.r, 2) for record in data]

        x_bar_avg = round(sum(x_bars) / len(x_bars), 2)
        r_bar = round(sum(ranges) / len(ranges), 2)

        # Constants for n=5 subgroup size
        a2, d3, d4 = 0.58, 0, 2.11

        # Calculate control limits with rounding
        ucl_x_bar = round(x_bar_avg + (a2 * r_bar), 2)
        lcl_x_bar = round(x_bar_avg - (a2 * r_bar), 2)
        ucl_r = round(d4 * r_bar, 2)
        lcl_r = round(d3 * r_bar, 2)

        return {
            'x_bar_avg': x_bar_avg,
            'r_bar': r_bar,
            'ucl_x_bar': ucl_x_bar,
            'lcl_x_bar': lcl_x_bar,
            'ucl_r': ucl_r,
            'lcl_r': lcl_r
        }

    @classmethod
    def calculate_capability_indices(cls, machine=None):
        """
        Calculate capability indices, optionally for a specific machine
        """
        query = cls.objects
        
        # If machine is provided, filter by it
        if machine:
            query = query.filter(machine=machine)
            
        data = query.all()
        
        if not data.exists():
            return {
                'cp': 0,
                'cpk': 0,
                'std_dev': 0
            }

        latest_record = data.latest('date')
        x_bars = [record.x_bar for record in data]
        
        # Calculate standard deviation using R-bar method
        r_bar = round(query.aggregate(Avg('r'))['r__avg'] or 0, 2)
        
        # Add safety check to prevent division by zero
        if r_bar == 0:
            return {
                'cp': 0,
                'cpk': 0,
                'std_dev': 0,
                'usl': latest_record.usl,
                'lsl': latest_record.lsl
            }
        
        std_dev = round(r_bar / 2.326, 2)  # d2 constant for n=5 is 2.326
        
        x_bar_avg = round(sum(x_bars) / len(x_bars), 2)
        
        # Use the specification limits from the latest record
        usl = latest_record.usl
        lsl = latest_record.lsl
        
        # Add safety checks for division by zero
        if std_dev == 0:
            return {
                'cp': 0,
                'cpk': 0,
                'std_dev': 0,
                'usl': usl,
                'lsl': lsl
            }
        
        # Calculate capability indices with Excel methodology
        cp = round((usl - lsl) / (6 * std_dev), 2)
        cpu = round((usl - x_bar_avg) / (3 * std_dev), 2)
        cpl = round((x_bar_avg - lsl) / (3 * std_dev), 2)
        cpk = round(min(cpu, cpl), 2)

        return {
            'cp': cp,
            'cpk': cpk,
            'std_dev': std_dev,
            'usl': usl,
            'lsl': lsl
        }
        
    @classmethod
    def check_special_causes(cls, data_points, mean, std_dev):
        """
        Check for special cause variations in control chart data.
        
        Args:
            data_points (list): List of dictionaries containing date and x_bar values
            mean (float): Mean value of the x_bar measurements
            std_dev (float): Standard deviation of the x_bar measurements
        
        Returns:
            list: List of detected violations with details
        """
        if not data_points or std_dev == 0:
            return []
            
        violations = []
        
        # Convert data_points if needed to ensure each point has date, x_bar
        formatted_points = []
        for point in data_points:
            if isinstance(point, dict) and 'date' in point and 'x_bar' in point:
                formatted_points.append(point)
        
        if not formatted_points:
            return []
        
        # Sort points by date
        formatted_points.sort(key=lambda x: x['date'])
        
        def is_outside_std_dev(point, multiplier):
            """Check if a point is outside specified standard deviation limits"""
            return abs(point['x_bar'] - mean) > (std_dev * multiplier)
        
        def is_same_side(point, reference_point):
            """Check if two points are on the same side of the mean"""
            return (point['x_bar'] > mean) == (reference_point['x_bar'] > mean)
        
        # Rule A: Points beyond 3 sigma
        for i, point in enumerate(data_points):
            if is_outside_std_dev(point, 3):
                violations.append({
                    'rule': 'A',
                    'index': i,
                    'message': '1 point more than 3 standard deviations from centerline',
                    'date': point['date'],
                    'machine_id': point.get('machine_id'),
                    'value': point['x_bar'],
                    'severity': 'high'
                })
        
        # Rule B: 7 points in a row on same side
        for i in range(len(data_points) - 6):
            sequence = data_points[i:i+7]
            if all(p['x_bar'] > mean for p in sequence) or all(p['x_bar'] < mean for p in sequence):
                violations.append({
                    'rule': 'B',
                    'index': i,
                    'message': '7 points in a row on same side of centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'machine_id': sequence[0].get('machine_id'),
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'high'
                })
        # Rule C: 6 points in a row, increasing or decreasing
        for i in range(len(formatted_points) - 5):
            sequence = formatted_points[i:i+6]
            x_bars = [p['x_bar'] for p in sequence]
            
            increasing = True
            for j in range(len(x_bars)-1):
                if x_bars[j] >= x_bars[j+1]:
                    increasing = False
                    break
                    
            decreasing = True
            for j in range(len(x_bars)-1):
                if x_bars[j] <= x_bars[j+1]:
                    decreasing = False
                    break
            
            if increasing or decreasing:
                violations.append({
                    'rule': 'C',
                    'index': i,
                    'message': '6 points in a row, all increasing or decreasing',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': x_bars,
                    'severity': 'medium',
                    'trend': 'increasing' if increasing else 'decreasing'
                })
        
        # Rule E: 2 out of 3 points > 2 standard deviations (same side)
        for i in range(len(formatted_points) - 2):
            sequence = formatted_points[i:i+3]
            above_2sigma = [p for p in sequence if p['x_bar'] > mean + 2*std_dev]
            below_2sigma = [p for p in sequence if p['x_bar'] < mean - 2*std_dev]
            
            if len(above_2sigma) >= 2 or len(below_2sigma) >= 2:
                violations.append({
                    'rule': 'E',
                    'index': i,
                    'message': '2 out of 3 points > 2 standard deviations from centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'high'
                })
                
        # Rule F: 4 out of 5 points > 1 standard deviation (same side)
        for i in range(len(formatted_points) - 4):
            sequence = formatted_points[i:i+5]
            above_1sigma = [p for p in sequence if p['x_bar'] > mean + std_dev]
            below_1sigma = [p for p in sequence if p['x_bar'] < mean - std_dev]
            
            if len(above_1sigma) >= 4 or len(below_1sigma) >= 4:
                violations.append({
                    'rule': 'F',
                    'index': i,
                    'message': '4 out of 5 points > 1 standard deviation from centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'medium'
                })
                
        # Rule H: 8 points > 1 standard deviation from centerline (either side)
        for i in range(len(formatted_points) - 7):
            sequence = formatted_points[i:i+8]
            outside_1sigma = [p for p in sequence if abs(p['x_bar'] - mean) > std_dev]
            
            if len(outside_1sigma) == len(sequence):
                violations.append({
                    'rule': 'H',
                    'index': i,
                    'message': '8 points in a row > 1 standard deviation from centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'high'
                })
                
        return violations
    
    @classmethod
    def get_monthly_statistics_with_violations(cls, year, month, machine=None):
        """
        Get monthly statistics including special cause violations, optionally for a specific machine
        """
        query = cls.objects.filter(
            date__year=year,
            date__month=month
        )
        
        # If machine is provided, filter by it
        if machine:
            query = query.filter(machine=machine)
            
        monthly_stats = query.order_by('date').values('date', 'machine', 'x_bar', 'r')
        
        if not monthly_stats:
            return [], []
        
        data_points = list(monthly_stats)
        
        # If we have a specific machine, analyze directly
        if machine:
            # Already filtered by machine, proceed normally
            x_bars = [point['x_bar'] for point in data_points]
            mean = sum(x_bars) / len(x_bars)
            std_dev = math.sqrt(sum((x - mean) ** 2 for x in x_bars) / len(x_bars))
            
            violations = cls.check_special_causes(data_points, mean, std_dev)
            return data_points, violations
        else:
            # Group by machine and analyze each group separately
            all_violations = []
            machine_groups = {}
            
            # Group data by machine
            for point in data_points:
                machine_id = point['machine']
                if machine_id not in machine_groups:
                    machine_groups[machine_id] = []
                machine_groups[machine_id].append(point)
            
            # Analyze each machine separately
            for machine_id, points in machine_groups.items():
                x_bars = [point['x_bar'] for point in points]
                mean = sum(x_bars) / len(x_bars)
                std_dev = math.sqrt(sum((x - mean) ** 2 for x in x_bars) / len(x_bars))
                
                machine_violations = cls.check_special_causes(points, mean, std_dev)
                all_violations.extend(machine_violations)
            
            return data_points, all_violations

# ----------------------------------------------------------------+

from django.db import models
from django.utils import timezone
from datetime import date
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import time as datetime_time

class StartUpCheckSheet(models.Model):
    
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    # General Information
    qsf_document = models.ForeignKey(QSF, on_delete=models.CASCADE, related_name='StartUpCheckSheet', null=True, blank=True)
    doc_number = models.CharField(max_length=20, default="QSF 12-05", null=True, blank=True)
    
    rev_number = models.CharField(max_length=20, default="Rev 09 ", null=True, blank=True)
    
    rev_date = models.DateField(default=date(2024, 11, 10), null=True, blank=True)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES, blank=True, null=True)
    # Time field is already present
    time = models.TimeField(default=timezone.now, blank=True)
    revision_no = models.IntegerField(verbose_name="Rev. No.", null=True, blank=True)    
    effective_date = models.DateField(verbose_name="Eff. Date", default=timezone.now, blank=True)
    process_machine = models.ForeignKey(ProcessMachineMapping, on_delete=models.CASCADE, related_name='StartUpCheckSheet', null=True, blank=True)   
    machine_name = models.CharField(max_length=100, null=True, blank=True)
    control_number = models.CharField(max_length=100, null=True, blank=True)  
    process_no = models.CharField(max_length=100, null=True, blank=True)     
    process_operation = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation", null=True, blank=True)
    month = models.DateField(default=timezone.now, null=True, blank=True)
    # Choices for Checkpoints
    OKAY_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('not applicable','Not Applicable'),
        ('not available','Not AVAILABLE'),
    ]
    OKAY_CHOICES2 = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),

    ]
    

    # Checkpoints with choices
    checkpoint_1 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 1")
    checkpoint_2 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 2")
    checkpoint_3 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 3")
    checkpoint_4 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 4")
    checkpoint_5 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 5")
    checkpoint_6 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 6")
    checkpoint_7 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 7")
    checkpoint_8 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 8")
    checkpoint_9 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 9")
    checkpoint_10 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 10")
    checkpoint_11 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 11")
    checkpoint_12 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 12")
    checkpoint_13 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 13")
    checkpoint_14 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 14")
    checkpoint_15 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 15")
    checkpoint_16 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 16")
    checkpoint_17 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 17")
    checkpoint_18 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 18")
    checkpoint_19 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 19")
    checkpoint_20 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 20")
    checkpoint_21 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 21")
    checkpoint_22 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 22")
    checkpoint_23 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 23")
    checkpoint_24 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 24")
    checkpoint_25 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 25")
    checkpoint_26 = models.CharField(max_length=60, choices=OKAY_CHOICES, verbose_name="Check Point 26",blank=True,null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True)    
    # defects = models.TextField(blank=True)
    verified_by = models.CharField(max_length=60, choices=OKAY_CHOICES2, default='✔', blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Start Up Check Sheet"
        verbose_name_plural = "Start Up Check Sheets"

    # Checkpoint info dictionary remains unchanged
    CHECKPOINT_INFO = {
        1: {
            'name': 'Equipment Safety Guards',
            'description': 'Verify all safety guards and emergency stops are functional',
            'criteria': 'All safety devices must be operational and properly installed'
        },
        2: {
            'name': 'Power Supply System',
            'description': 'Confirm proper voltage and connections',
            'criteria': 'Voltage within specified range, all connections secure'
        },
        3: {
            'name': 'Machine Cleanliness',
            'description': 'Check machine cleanliness and surrounding area',
            'criteria': 'No debris, proper cleaning completed'
        },
        4: {
            'name': 'Oil Level Check',
            'description': 'Verify oil levels in all required components',
            'criteria': 'Oil levels within specified range markers'
        },
        5: {
            'name': 'Air Pressure System',
            'description': 'Check air pressure systems and connections',
            'criteria': 'Pressure readings within operational range'
        },
        6: {
            'name': 'Control Panel Function',
            'description': 'Verify all control panel buttons and displays',
            'criteria': 'All indicators and controls responding correctly'
        },
        7: {
            'name': 'Sensor Systems',
            'description': 'Check all sensor operations and calibration',
            'criteria': 'Sensors providing accurate readings and responses'
        },
        8: {
            'name': 'Cooling System',
            'description': 'Verify cooling system operation and fluid levels',
            'criteria': 'Proper coolant levels and circulation'
        },
        9: {
            'name': 'Hydraulic System',
            'description': 'Check hydraulic system pressure and fluid levels',
            'criteria': 'Hydraulic pressure and fluid levels within range'
        },
        10: {
            'name': 'Belt and Chain Tension',
            'description': 'Inspect all belts and chains for proper tension',
            'criteria': 'Correct tension and no visible damage'
        },
        11: {
            'name': 'Lubrication Points',
            'description': 'Check all lubrication points and systems',
            'criteria': 'All points properly lubricated'
        },
        12: {
            'name': 'Tool Condition',
            'description': 'Inspect condition of all cutting tools and attachments',
            'criteria': 'Tools sharp and in good condition'
        },
        13: {
            'name': 'Ventilation System',
            'description': 'Check ventilation and exhaust systems',
            'criteria': 'Proper airflow and filter condition'
        },
        14: {
            'name': 'Material Feed System',
            'description': 'Verify material feeding mechanism operation',
            'criteria': 'Smooth operation without obstructions'
        },
        15: {
            'name': 'Waste Collection',
            'description': 'Check waste collection systems and containers',
            'criteria': 'Proper waste removal and container condition'
        },
        16: {
            'name': 'Emergency Systems',
            'description': 'Test emergency stop and safety systems',
            'criteria': 'All emergency systems responding correctly'
        },
        17: {
            'name': 'Calibration Check',
            'description': 'Verify machine calibration and alignment',
            'criteria': 'All measurements within specified tolerances'
        },
        18: {
            'name': 'Electrical Connections',
            'description': 'Inspect all electrical connections and wiring',
            'criteria': 'No loose connections or damaged wiring'
        },
        19: {
            'name': 'Warning Indicators',
            'description': 'Check all warning lights and indicators',
            'criteria': 'All indicators functioning properly'
        },
        20: {
            'name': 'Operating Temperature',
            'description': 'Verify normal operating temperature range',
            'criteria': 'Temperature within specified limits'
        },
        21: {
            'name': 'Safety Equipment',
            'description': 'Check availability and condition of safety equipment',
            'criteria': 'All safety equipment present and functional'
        },
        22: {
            'name': 'Documentation',
            'description': 'Verify presence of required documentation',
            'criteria': 'All necessary documents available and current'
        },
        23: {
            'name': 'Communication System',
            'description': 'Test machine communication systems',
            'criteria': 'All communication functions operational'
        },
        24: {
            'name': 'Auxiliary Systems',
            'description': 'Check all auxiliary equipment and attachments',
            'criteria': 'All auxiliary systems functioning correctly'
        },
        25: {
            'name': 'Final Inspection',
            'description': 'Overall equipment condition assessment',
            'criteria': 'All parameters within acceptable ranges'
        }
    }

    def save(self, *args, **kwargs):
        """
        Save method with enhanced debugging and robust process/machine handling
        """
        print("\n=== StartUpCheckSheet SAVE METHOD BEGIN ===")
        print(f"PK: {self.pk}, Is New Record: {self.pk is None}")
        
        # Auto-determine shift based on time
        if hasattr(self, 'time') and self.time:
            current_time = self.time
            print(f"Current time: {current_time}")
            
            from datetime import time as datetime_time
            
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            else:
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                self.shift = 'A' if abs(morning_diff) < abs(evening_diff) else 'B'
            
            print(f"Determined shift: {self.shift}")
        else:
            print("Time field not available, shift not automatically determined")

        # Debug input data
        request = getattr(self, 'request', None)
        print(f"Request available: {request is not None}")
        
        browser_key = None
        if request:
            browser_key = request.session.get('browser_key')
            print(f"Browser key from session: {browser_key}")
        
        # Direct assignments - handle explicitly set fields
        print("\n=== DIRECT FIELD ASSIGNMENTS ===")
        if hasattr(self, '_direct_machine_name') and self._direct_machine_name:
            print(f"Using directly assigned machine_name: {self._direct_machine_name}")
            self.machine_name = self._direct_machine_name
        
        if hasattr(self, '_direct_process_no') and self._direct_process_no:
            print(f"Using directly assigned process_no: {self._direct_process_no}")
            self.process_no = self._direct_process_no
        
        # Try to get machine from browser login if new record
        if self.pk is None and browser_key:
            print("\n=== TRYING TO GET MACHINE FROM BROWSER KEY ===")
            try:
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    machine = active_login.machine
                    print(f"Found active machine: {machine.name}")
                    
                    # Process machine lookup
                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name
                    ).first()
                    
                    if process_machine:
                        print(f"Found process machine mapping: {process_machine.machine_name}")
                        self.process_machine = process_machine
                    else:
                        print(f"No process machine mapping found for {machine.name}")
                        # Create a direct assignment for debugging
                        self.machine_name = machine.name
                else:
                    print("No active login found for this browser key")
            except Exception as e:
                print(f"Error getting machine from browser key: {str(e)}")
        
        # Auto-populate from QSF document
            
        # Auto-populate from process_machine
        print("\n=== PROCESS MACHINE PROCESSING ===")
        if self.process_machine:
            print(f"Using process_machine: {self.process_machine}")
            print(f"Before: machine_name={self.machine_name}, control_number={self.control_number}, process_no={self.process_no}")
            
            self.machine_name = self.process_machine.machine_name
            self.control_number = self.process_machine.control_number
            self.process_no = self.process_machine.process_no
            
            print(f"After: machine_name={self.machine_name}, control_number={self.control_number}, process_no={self.process_no}")
            
            # Try to find a matching machine_location
            print("\n=== MACHINE LOCATION LOOKUP ===")
            try:
                print(f"Looking for location with process: {self.process_machine.process}")
                
                # First try exact match
                location = MachineLocation.objects.filter(
                    location_name=self.process_machine.process
                ).first()
                
                if location:
                    print(f"Found exact match location: {location}")
                    self.process_operation = location
                else:
                    # Try substring match
                    print("No exact match, trying substring match")
                    location = MachineLocation.objects.filter(
                        location_name__icontains=self.process_machine.process
                    ).first()
                    
                    if location:
                        print(f"Found substring match location: {location}")
                        self.process_operation = location
                    else:
                        print("No substring match found")
            except Exception as e:
                print(f"Error finding machine location: {str(e)}")
        else:
            print("No process_machine available")
        
        # Make sure process_operation is set
        print("\n=== ENSURING PROCESS OPERATION IS SET ===")
        if not self.process_operation:
            print("No process_operation set, looking for a default")
            try:
                # List all available locations for debugging
                all_locations = MachineLocation.objects.all()
                print(f"Available locations ({all_locations.count()}):")
                for loc in all_locations[:5]:  # Show first 5 for debugging
                    print(f" - {loc.id}: {loc}")
                
                # Try to get a default location
                default_location = all_locations.first()
                if default_location:
                    print(f"Using default location: {default_location}")
                    self.process_operation = default_location
                else:
                    print("No machine locations exist in database")
            except Exception as e:
                print(f"Error finding default machine location: {str(e)}")
        else:
            print(f"process_operation is already set: {self.process_operation}")
        
        # Handle manager assignment
        if not self.manager and hasattr(self, 'request') and request and hasattr(request, 'user'):
            self.manager = request.user
            print(f"Set manager to current user: {self.manager}")
        
        # Prepare final state before save
        print("\n=== FINAL STATE BEFORE SAVE ===")
        print(f"process_machine: {self.process_machine}")
        print(f"machine_name: {self.machine_name}")
        print(f"control_number: {self.control_number}")
        print(f"process_no: {self.process_no}")
        print(f"process_operation: {self.process_operation}")
        print(f"shift: {self.shift}")
        
        # Call parent save method
        try:
            super().save(*args, **kwargs)
            print("Save successful")
            
            # Send notifications for failed checkpoints
            self._send_notifications_for_failed_checkpoints()
        except Exception as e:
            print(f"ERROR saving record: {str(e)}")
            raise  # Re-raise the exception after logging
        
        print("=== StartUpCheckSheet SAVE METHOD END ===\n")
    
                
    def _send_notifications_for_failed_checkpoints(self):
        """Extracted method to send notifications for failed checkpoints"""
        channel_layer = get_channel_layer()
        
        checkpoints = [
            self.checkpoint_1, self.checkpoint_2, self.checkpoint_3, self.checkpoint_4,
            self.checkpoint_5, self.checkpoint_6, self.checkpoint_7, self.checkpoint_8,
            self.checkpoint_9, self.checkpoint_10, self.checkpoint_11, self.checkpoint_12,
            self.checkpoint_13, self.checkpoint_14, self.checkpoint_15, self.checkpoint_16,
            self.checkpoint_17, self.checkpoint_18, self.checkpoint_19, self.checkpoint_20,
            self.checkpoint_21, self.checkpoint_22, self.checkpoint_23, self.checkpoint_24,
            self.checkpoint_25
        ]

        for i, checkpoint in enumerate(checkpoints, start=1):
            if checkpoint == '✘':
                notification = self.get_notification_message(i, checkpoint)
                async_to_sync(channel_layer.group_send)('test', notification)
    
    def get_notification_message(self, checkpoint_number, status):
        """Generate structured notification message"""
        checkpoint_info = self.CHECKPOINT_INFO.get(checkpoint_number, {
            'name': f'Checkpoint {checkpoint_number}',
            'description': 'General equipment check',
            'criteria': 'Must meet operational standards'
        })

        return {
            'type': 'chat_message',
            'message': {
                # Record identification
                'record_id': self.pk,
                'alert_type': 'startup_checksheet_alert',
                
                # Document control information
                'revision_no': self.revision_no or 'Not Specified',
                'process_operation': str(self.process_operation) if self.process_operation else 'Not Specified',
                'effective_date': self.effective_date.strftime('%Y-%m-%d') if self.effective_date else 'Not Specified',
                
                # Checkpoint details
                'checkpoint': {
                    'number': checkpoint_number,
                    'name': checkpoint_info['name'],
                    'description': checkpoint_info['description'],
                    'criteria': checkpoint_info['criteria'],
                    'status': status
                },
                
                # Alert metadata
                'needs_attention': True,
                'severity': 'high' if status == '✘' else 'normal',
                'check_time': timezone.now().strftime('%H:%M:%S'),
                
                # Management information
                'manager': str(self.manager) if self.manager else 'Not Assigned',
                'month': self.month.strftime('%B %Y') if self.month else 'Not Specified',
                
                # Additional context
                'shift': self.shift or 'Not Specified',
                'department': str(getattr(self, 'department', 'Not Specified'))
            }
        }
                
    def __str__(self):
        revision_display = self.revision_no if self.revision_no else "No Rev"
        date_display = self.effective_date.strftime('%Y-%m-%d') if self.effective_date else "No Date"
        return f"Start Up Check Sheet {revision_display} - {date_display}"


# ---------------------------------------------------------------------

from django.db import models
from django.utils import timezone
import math
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import time as datetime_time

from django.db import models
from django.utils import timezone
import math
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import time as datetime_time

class PChartData(models.Model):
    # Document info fields
    doc_number = models.CharField(max_length=20, default="QSF 12-05", null=True, blank=True)
    rev_number = models.CharField(max_length=20, default="Rev 09 ", null=True, blank=True)

    # Process machine mapping connection
    process_machine = models.ForeignKey('ProcessMachineMapping', on_delete=models.CASCADE, 
                                       related_name='pchart_data', null=True, blank=True)
    
    # Auto-filled fields (will be populated from process_machine)
    location = models.CharField(max_length=200, null=True, blank=True)
    part_number_and_name = models.CharField(max_length=200, null=True, blank=True)
    operation_number_and_stage_name = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    
    # Shift field
    shift = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')], null=True, blank=True)
    time = models.TimeField(default=timezone.now, blank=True)
    
    # Changed from month to date to allow for daily entries
    date = models.DateField(default=timezone.now,blank=True)
    date_control_limits_calculated = models.DateField(default=timezone.now,blank=True)
    
    # Only these two fields will be requested from user
    sample_size = models.IntegerField()
    nonconforming_units = models.IntegerField()
    
    # Auto-calculated fields
    proportion = models.FloatField(null=True, blank=True)
    ucl_p = models.FloatField(null=True, blank=True)
    lcl_p = models.FloatField(null=True, blank=True)
    history = HistoricalRecords()
    
    @property
    def month(self):
        """For compatibility with existing code"""
        return self.date.replace(day=1)
    
    def calculate_control_limits(self):
        try:
            # Calculate proportion (p-bar)
            self.proportion = self.nonconforming_units / self.sample_size if self.sample_size > 0 else None
            
            # Calculate P-Chart limits for this individual entry
            # Note: In the view, we'll calculate monthly limits separately
            if self.sample_size > 0 and self.proportion is not None and 0 <= self.proportion <= 1:
                p_std = math.sqrt((self.proportion * (1 - self.proportion)) / self.sample_size)
                self.ucl_p = min(1, self.proportion + 3 * p_std)
                self.lcl_p = max(0, self.proportion - 3 * p_std)

        except (ZeroDivisionError, ValueError) as e:
            print(f"Error calculating control limits: {e}")

    def check_control_limits(self):
        """Check for out-of-control conditions"""
        violations = []
        
        if self.proportion is not None:
            # P-Chart violations
            if self.ucl_p is not None and self.proportion > self.ucl_p:
                violations.append(f"P-Chart: Proportion ({self.proportion:.4f}) exceeds UCL ({self.ucl_p:.4f})")
            if self.lcl_p is not None and self.proportion < self.lcl_p and self.lcl_p > 0:
                violations.append(f"P-Chart: Proportion ({self.proportion:.4f}) below LCL ({self.lcl_p:.4f})")

        return violations

    def get_notification_message(self, violations):
        """Generate structured notification message"""
        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'alert_type': 'p_chart_alert',
                'location': self.location,
                'part_info': self.part_number_and_name,
                'operation': self.operation_number_and_stage_name,
                'department': self.department,
                'date': self.date.strftime('%Y-%m-%d'),
                'metrics': {
                    'sample_size': self.sample_size,
                    'nonconforming': self.nonconforming_units,
                    'proportion': round(self.proportion, 4) if self.proportion else None,
                },
                'control_limits': {
                    'p_chart': {
                        'ucl': round(self.ucl_p, 4) if self.ucl_p else None,
                        'lcl': round(self.lcl_p, 4) if self.lcl_p else None
                    }
                },
                'violations': violations,
                'needs_attention': bool(violations),
                'severity': 'high' if len(violations) > 1 else 'medium' if violations else 'low',
                'doc_number': self.doc_number,
                'rev_number': self.rev_number,
                'shift': self.shift
            }
        }

    def save(self, *args, **kwargs):
        print("\n=== PChartData SAVE METHOD BEGIN ===")
        print(f"PK: {self.pk}, Is New Record: {self.pk is None}")
        
        # Auto-determine shift based on time
        if hasattr(self, 'time') and self.time:
            current_time = self.time
            print(f"Current time: {current_time}")
            
            # Define shift time ranges
            shift_a_start = datetime_time(7, 30)  # 07:30
            shift_a_end = datetime_time(16, 0)    # 16:00
            shift_b_start = datetime_time(16, 30) # 16:30
            
            # Convert current_time to datetime.time if it's a datetime
            if hasattr(current_time, 'time'):
                current_time = current_time.time()
            
            if shift_a_start <= current_time <= shift_a_end:
                self.shift = 'A'
            elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
                self.shift = 'B'
            else:
                morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
                evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
                
                self.shift = 'A' if abs(morning_diff) < abs(evening_diff) else 'B'
            
            print(f"Determined shift: {self.shift}")
        
        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        print(f"Request available: {request is not None}")
        
        # Try to get machine from browser login if new record
        if is_new and request:
            browser_key = request.session.get('browser_key')
            print(f"Browser key from session: {browser_key}")
            
            if browser_key:
                try:
                    from machineapp.models import MachineLoginTracker
                    active_login = MachineLoginTracker.objects.filter(
                        browser_key=browser_key,
                        is_active=True
                    ).order_by('-created_at').first()
                    
                    if active_login:
                        machine = active_login.machine
                        print(f"Found active machine: {machine.name}")
                        
                        # Process machine lookup
                        process_machine = ProcessMachineMapping.objects.filter(
                            process=machine.name
                        ).first()
                        
                        if process_machine:
                            print(f"Found process machine mapping: {process_machine.machine_name}")
                            self.process_machine = process_machine
                        else:
                            print(f"No process machine mapping found for {machine.name}")
                    else:
                        print("No active login found for this browser key")
                except Exception as e:
                    print(f"Error getting machine from browser key: {str(e)}")
        
        # Auto-populate fields from process_machine
        if self.process_machine:
            print(f"Using process_machine: {self.process_machine}")
            print("Before populating from process_machine:")
            print(f"location: {self.location}")
            print(f"part_number_and_name: {self.part_number_and_name}")
            print(f"operation_number_and_stage_name: {self.operation_number_and_stage_name}")
            print(f"department: {self.department}")
            
            # Map fields from process_machine to PChartData fields
            # Adjust these mappings based on your ProcessMachineMapping model fields
            self.location = self.process_machine.process or self.location
            self.part_number_and_name = self.process_machine.part_name or self.part_name
            self.operation_number_and_stage_name = self.process_machine.station or self.operation_number_and_stage_name
            self.department = self.process_machine.process_no 
            
            print("After populating from process_machine:")
            print(f"location: {self.location}")
            print(f"part_number_and_name: {self.part_number_and_name}")
            print(f"operation_number_and_stage_name: {self.operation_number_and_stage_name}")
            print(f"department: {self.department}")
        else:
            print("No process_machine available for auto-population")
        
        # Calculate control limits
        self.calculate_control_limits()
        
        print("Final state before save:")
        print(f"location: {self.location}")
        print(f"part_number_and_name: {self.part_number_and_name}")
        print(f"operation_number_and_stage_name: {self.operation_number_and_stage_name}")
        print(f"department: {self.department}")
        print(f"shift: {self.shift}")
        print(f"proportion: {self.proportion}")
        print(f"ucl_p: {self.ucl_p}")
        print(f"lcl_p: {self.lcl_p}")
        
        # Save the record
        try:
            super().save(*args, **kwargs)
            print("Save successful")
            
            # Check for violations and send notification
            violations = self.check_control_limits()
            if violations:
                print(f"Found violations: {violations}")
                channel_layer = get_channel_layer()
                notification = self.get_notification_message(violations)
                async_to_sync(channel_layer.group_send)('test', notification)
            else:
                print("No violations detected")
        except Exception as e:
            print(f"ERROR saving record: {str(e)}")
            raise  # Re-raise the exception after logging
        
        print("=== PChartData SAVE METHOD END ===\n")
        
        
        
        
        
        
        
#   
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class PCBPanelInspectionRecord(models.Model):
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    
    STATUS_CHOICES = [
        ('OK', 'OK'),
        ('Not OK', 'Not OK'),
    ]
    
    # Document information
    doc_number = models.CharField(max_length=20, default="A-SMT-07", blank=True)
    rev_number = models.CharField(max_length=20, default="00", blank=True)
    doc_date = models.DateField(default=timezone.now, blank=True)
    
    # Basic information
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES, blank=True, null=True)
    
    # PCB information
    pcb_number = models.CharField(max_length=100, verbose_name="PCB No. / Rev.")
    customer = models.CharField(max_length=100)
    pcb_batch_code = models.CharField(max_length=100)
    inspection_qty = models.IntegerField(default=5, help_text="Number of pieces inspected")
    
    # Inspection criteria
    no_masking_issue = models.CharField(max_length=10, choices=STATUS_CHOICES, help_text="No peel off, No foreign material")
    no_dust_contamination = models.CharField(max_length=10, choices=STATUS_CHOICES, help_text="No Dust or contamination on PCB Panel")
    no_track_damage = models.CharField(max_length=10, choices=STATUS_CHOICES, help_text="No Track cut / damage mark on PCB Panel")
    
    # Process information
    process_machine = models.ForeignKey(
        'ProcessMachineMapping', 
        on_delete=models.CASCADE, 
        related_name='PCBPanelInspectionRecords',
        null=True, 
        blank=True
    )
    station = models.CharField(max_length=100, blank=True)
    line = models.CharField(max_length=100, blank=True)
    plant = models.CharField(max_length=100, blank=True)
    
    # Accountability
    operator_name = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='pcb_inspections', 
        blank=True, 
        null=True
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='pcb_verifications', 
        blank=True, 
        null=True
    )
    remarks = models.TextField(blank=True, null=True)
    
    # Tracking changes
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "PCB Panel Inspection Record"
        verbose_name_plural = "PCB Panel Inspection Records"
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-populate fields based on logged-in machine
        and auto-determine shift based on time.
        """
        from datetime import datetime
        
        # Auto-determine shift based on time
        current_time = datetime.now().time()
        
        # Define shift time ranges
        from datetime import time as datetime_time
        
        # Shift definitions - assuming standard 8-hour shifts
        shift_a_start = datetime_time(6, 0)   # 06:00
        shift_a_end = datetime_time(14, 0)    # 14:00
        shift_b_start = datetime_time(14, 0)  # 14:00
        shift_b_end = datetime_time(22, 0)    # 22:00
        # Shift C is from 22:00 to 06:00
        
        # Determine shift
        if shift_a_start <= current_time < shift_a_end:
            self.shift = 'A'
        elif shift_b_start <= current_time < shift_b_end:
            self.shift = 'B'
        else:
            self.shift = 'C'
        
        # Check if this is a new record
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name  # Adjust field name if needed
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
                        self.station = process_machine
                        self.line = process_machine.process  # Assuming process can be used as line
                        print(process_machine , 'hyyy')  
        
        # Handle operator assignment if available
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        """String representation of the PCB inspection record."""
        return f"PCB Inspection {self.pcb_number} - {self.date}" 
    
    
    
    
    
    
    
#-----------------------------------------
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class ReworkAnalysisRecord(models.Model):
    STATUS_CHOICES = [
        ('Rework', 'Rework'),
        ('Scrap', 'Scrap'),
    ]
    
    VERIFICATION_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    ]
    
    # Document information
    doc_number = models.CharField(max_length=20, default="QSF-22-02", blank=True)
    rev_number = models.CharField(max_length=20, default="03", blank=True)
    rev_date = models.DateField(default=timezone.datetime(2023, 12, 29).date(), blank=True)
    
    # General information
    month = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=4, blank=True)
    department_name = models.CharField(max_length=100, blank=True)
    process = models.CharField(max_length=100, blank=True)
    
    # Record details
    sr_no = models.PositiveIntegerField(blank=True, null=True)
    problem_found_date = models.DateField(default=timezone.now)
    part_received_date = models.DateField(default=timezone.now)
    line_shift = models.CharField(max_length=50, verbose_name="Line/Shift")
    part_identification_no = models.CharField(max_length=100, verbose_name="Part Identification No.")
    short_code = models.CharField(max_length=50, blank=True)
    problem_found_stage = models.CharField(max_length=100)
    defects_details = models.TextField(blank=True, null=True)
    defect_location_on_pcb = models.CharField(max_length=100)
    defect_qty = models.PositiveIntegerField(default=1)
    
    # Analysis details
    analysis_date = models.DateField(default=timezone.now)
    child_part_im_code = models.CharField(max_length=100, blank=True, verbose_name="Child Part IM Code")
    component_package_size = models.CharField(max_length=50, blank=True)
    reason_for_defect = models.TextField(blank=True, null=True)
    
    # Rework details
    rework_details = models.TextField(blank=True, null=True)
    rework_date = models.DateField(default=timezone.now)
    rework_done_by = models.CharField(max_length=100)
    part_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Rework')
    part_re_verification = models.CharField(
        max_length=5, 
        choices=VERIFICATION_CHOICES, 
        default='Pass',
        verbose_name="Part Re-verification Status"
    )
    
    # Verification
    verified_by = models.CharField(max_length=100, blank=True, verbose_name="Verified by (Line Supervisor)")
    remarks = models.TextField(blank=True, null=True)
    
    # Process machine relation (optional, if needed for system integration)
    process_machine = models.ForeignKey(
        'ProcessMachineMapping', 
        on_delete=models.SET_NULL, 
        related_name='rework_analyses',
        null=True, 
        blank=True
    )
    
    # Record creation/modification info
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='rework_records_created',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Rework Analysis Record"
        verbose_name_plural = "Rework Analysis Records"
        ordering = ['-problem_found_date', 'sr_no']
    
    def save(self, *args, **kwargs):
        # If sr_no is not set, auto-generate it based on the current month/year count
        if not self.sr_no:
            # Get records from the same month and year
            current_month = self.problem_found_date.month if self.problem_found_date else timezone.now().month
            current_year = self.problem_found_date.year if self.problem_found_date else timezone.now().year
            
            count = ReworkAnalysisRecord.objects.filter(
                problem_found_date__month=current_month,
                problem_found_date__year=current_year
            ).count()
            
            self.sr_no = count + 1
        
        # Auto-set month and year based on problem_found_date
        if self.problem_found_date:
            self.month = self.problem_found_date.strftime('%B')
            self.year = str(self.problem_found_date.year)
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If we have access to the request
        if request:
            # Set created_by to the current user
            if not self.pk:  # Only on creation
                self.created_by = request.user
            
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
                        # You might want to auto-populate other fields based on the machine
                        self.department_name = process_machine.station
                        self.process = process_machine.process
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Rework Analysis #{self.sr_no} - {self.part_identification_no} ({self.problem_found_date})"

 
# ----------------  

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class SolderPasteControl(models.Model):
    STATUS_CHOICES = [
        ('OK', 'OK'),
        ('NG', 'NG'),
    ]
    
    EXPIRY_STATUS_CHOICES = [
        ('Valid', 'Valid'),
        ('Expired', 'Expired'),
    ]
    
    # Solder paste specification (default values based on the document)
    paste_type = models.CharField(max_length=50, default="Lead Free Solder Paste")
    paste_make = models.CharField(max_length=50, default="Heraeus")
    part_number = models.CharField(max_length=50, default="F640SA30C5-89M30")
    alloy = models.CharField(max_length=100, default="Sn 96.5; Ag 3; Cu 0.5")
    mesh_type = models.CharField(max_length=100, default="Type 3 =25 -45 microns (325/=500mesh)")
    net_weight = models.CharField(max_length=20, default="500 Gms")
    paste_code = models.CharField(max_length=10, default="G1")
    
    # Entry information
    serial_number = models.CharField(max_length=20, verbose_name="S No G1-")
    
    # PSR Information
    psr_date = models.DateField(default=timezone.now, verbose_name="PSR Date")
    psr_number = models.CharField(max_length=20, verbose_name="PSR No.")
    
    # Validation checks
    make_status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='OK', verbose_name="Make Status")
    part_number_status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='OK', verbose_name="Part Number Status")
    alloy_status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='OK', verbose_name="Alloy Status")
    net_weight_status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='OK', verbose_name="Net Weight Status")
    
    # Lot information
    lot_number = models.CharField(max_length=50, verbose_name="Lot No")
    expiry_date = models.DateField()
    deep_storage_jar_number = models.CharField(max_length=50, verbose_name="Deep Storage Tubular Jar No.")
    
    # Removal for Thawing details
    thawing_date = models.DateField(blank=True, null=True, verbose_name="Thawing Date")
    thawing_time = models.TimeField(blank=True, null=True, verbose_name="Thawing Time")
    expiry_status = models.CharField(max_length=10, choices=EXPIRY_STATUS_CHOICES, default='Valid')
    thawing_sign = models.CharField(max_length=50, blank=True, verbose_name="Thawing Sign")
    
    # Paste mixing details
    mixing_date = models.DateField(blank=True, null=True, verbose_name="Mixing Date")
    mixing_time = models.TimeField(blank=True, null=True, verbose_name="Mixing Time")
    
    # First time use details
    first_use_date = models.DateField(blank=True, null=True, verbose_name="First Use Date")
    first_use_time = models.TimeField(blank=True, null=True, verbose_name="First Use Time")
    first_use_sign = models.CharField(max_length=50, blank=True, verbose_name="First Use Sign")
    
    # Second time use details
    second_use_date = models.DateField(blank=True, null=True, verbose_name="Second Use Date")
    second_use_time = models.TimeField(blank=True, null=True, verbose_name="Second Use Time")
    second_use_sign = models.CharField(max_length=50, blank=True, verbose_name="Second Use Sign")
    
    # Additional information
    remarks = models.TextField(blank=True)
    
    # Process machine relation (optional, if needed for system integration)
    process_machine = models.ForeignKey(
        'ProcessMachineMapping', 
        on_delete=models.SET_NULL, 
        related_name='solder_paste_controls',
        null=True, 
        blank=True
    )
    
    # Record creation/modification info
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='solder_paste_records_created',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    def get_use_period(self):
        """Calculate the use period based on dates"""
        if self.second_use_date:
            # Calculate from first to second use
            if self.first_use_date:
                days = (self.second_use_date - self.first_use_date).days
                return f"{days} days"
        elif self.first_use_date:
            # Calculate from thawing to first use
            if self.thawing_date:
                days = (self.first_use_date - self.thawing_date).days
                return f"{days} days"
        
        # If dates not available or no use yet
        return "Not used yet"
    
    def save(self, *args, **kwargs):
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If we have access to the request
        if request:
            # Set created_by to the current user on creation
            if not self.pk:  # Only on creation
                self.created_by = request.user
                
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                from machineapp.models import MachineLoginTracker
                active_login = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).order_by('-created_at').first()
                
                if active_login:
                    # Get the machine from the active login
                    machine = active_login.machine

                    process_machine = ProcessMachineMapping.objects.filter(
                        process=machine.name
                    ).first()
                    
                    if process_machine:
                        self.process_machine = process_machine
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Solder Paste Control"
        verbose_name_plural = "Solder Paste Controls"
        ordering = ['-psr_date', 'serial_number']
    
    def __str__(self):
        return f"Solder Paste Control: G1-{self.serial_number} ({self.psr_date})" 
    
    
    
    
    
    
    
# ------------------------------

class TipVoltageResistanceRecord(models.Model):
    SHIFT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]
    
    FREQ_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
        ('3rd', '3rd'),
        ('4th', '4th'),
    ]
    
    STATUS_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    
    # Document Information
    qsf_document = models.CharField(max_length=50,null=True, blank=True, default='QSF-12-09')
    
    
    process_machine = models.ForeignKey(ProcessMachineMapping, on_delete=models.CASCADE, related_name='TipVoltageResistanceRecords', null=True, blank=True)
    
    # Basic Information
    department = models.CharField(max_length=50, default="Production")
    operation = models.CharField(max_length=50, default="Rework")
    month_year = models.DateField(default=timezone.now)
    soldering_station_control_no = models.CharField(max_length=100, blank=True, null=True)
    
    # Measurement Details
    date = models.DateField(default=timezone.now)
    frequency = models.CharField(max_length=5, choices=FREQ_CHOICES)
    tip_voltage = models.FloatField(help_text="Should be less than 1V")
    tip_resistance = models.FloatField(help_text="Should be less than 10Ω")
    
    # Signatures
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tip_voltage_records_as_operator', blank=True, null=True)
    operator_signature = models.CharField(max_length=1, choices=STATUS_CHOICES, default='✔')
    supervisor_signature = models.CharField(max_length=1, choices=STATUS_CHOICES, default='✘')
    
    # Record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES, blank=True, null=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Tip Voltage & Resistance Record"
        verbose_name_plural = "Tip Voltage & Resistance Records"
        ordering = ['-date', 'frequency']
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-populate fields based on logged-in machine
        and auto-determine shift based on time.
        """
        from datetime import datetime, time as datetime_time
        
        # Auto-determine shift based on time
        current_time = datetime.now().time()
        
        # Define shift time ranges
        shift_a_start = datetime_time(7, 30)  # 07:30
        shift_a_end = datetime_time(16, 0)    # 16:00
        shift_b_start = datetime_time(16, 30) # 16:30
        
        # Check if time falls within Shift A
        if shift_a_start <= current_time <= shift_a_end:
            self.shift = 'A'
        # Check if time falls within Shift B (accounting for overnight)
        elif current_time >= shift_b_start or current_time <= datetime_time(0, 30):
            self.shift = 'B'
        # If time doesn't fit either shift, default to closest one
        else:
            # This handles gaps like 16:00-16:30
            morning_diff = (current_time.hour - shift_a_start.hour) * 60 + (current_time.minute - shift_a_start.minute)
            evening_diff = (current_time.hour - shift_b_start.hour) * 60 + (current_time.minute - shift_b_start.minute)
            
            if abs(morning_diff) < abs(evening_diff):
                self.shift = 'A'
            else:
                self.shift = 'B'
        
        # Check if this is a new record (not yet saved)
        is_new = self.pk is None
        
        # Get the current request from thread local if available
        request = getattr(self, 'request', None)
        
        # If this is a new record and we have access to the request
        if is_new and request:
            # Get browser key from session if logged into a machine
            browser_key = request.session.get('browser_key')
            
            if browser_key:
                # Try to find the active machine for this browser
                try:
                    from machineapp.models import MachineLoginTracker
                    active_login = MachineLoginTracker.objects.filter(
                        browser_key=browser_key,
                        is_active=True
                    ).order_by('-created_at').first()
                    
                    if active_login:
                        # Get the machine from the active login
                        machine = active_login.machine
                        
                        process_machine = ProcessMachineMapping.objects.filter(
                            process=machine.name  # Adjust field name if needed
                        ).first()
                        
                        if process_machine:
                            self.process_machine = process_machine
                            self.soldering_station_control_no = process_machine.control_number
                except Exception as e:
                    print(f"Error getting machine information: {e}")
        
        # Handle operator assignment if available
        if not self.operator and hasattr(self, 'request') and hasattr(self.request, 'user'):
            self.operator = self.request.user
            
        # Validate measurements
        if self.tip_voltage > 1.0:
            self.operator_signature = '✘'  # Mark as not OK if voltage exceeds 1V
            
        if self.tip_resistance > 10.0:
            self.operator_signature = '✘'  # Mark as not OK if resistance exceeds 10Ω
        
        # Call parent save method
        super().save(*args, **kwargs)
        
        # Send notification if measurements are out of range
        if self.tip_voltage > 1.0 or self.tip_resistance > 10.0:
            self._send_notification()
    
    def _send_notification(self):
        """
        Send notification about out-of-range measurements.
        """
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            issues = []
            if self.tip_voltage > 1.0:
                issues.append(f"Tip voltage out of range: {self.tip_voltage}V (should be <1V)")
            if self.tip_resistance > 10.0:
                issues.append(f"Tip resistance out of range: {self.tip_resistance}Ω (should be <10Ω)")
            
            severity = 'high' if len(issues) > 1 else 'medium'
            
            notification = {
                'type': 'chat_message',
                'message': {
                    'alert_type': 'tip_measurement_alert',
                    'record_id': self.pk,
                    'station_control_no': self.soldering_station_control_no,
                    'date': self.date.strftime('%Y-%m-%d'),
                    'frequency': self.frequency,
                    'shift': self.shift,
                    'issues': issues,
                    'severity': severity
                }
            }
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('test', notification)
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def __str__(self):
        return f"Tip Measurement: {self.soldering_station_control_no} - {self.date} ({self.frequency})"
 