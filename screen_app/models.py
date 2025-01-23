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
        ('DSL01_S01', 'DSL01_S01'),
        ('DSL01_S02', 'DSL01_S02'),
        ('DSL01_S03', 'DSL01_S03'),
        ('DSL01_S04', 'DSL01_S04'),
        ('DSL01_S05', 'DSL01_S05'),
        ('DSL01_S06', 'DSL01_S06'),
        ('DSL01_S07', 'DSL01_S07'),
        ('DSL01_S08', 'DSL01_S08'),
        ('DSL01_S09', 'DSL01_S09'),
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

#  PDFs
# ----------------------------------------------------------------
# FixtureCleaningRecord
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

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

    TAG_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    modified_TAG_CHOICES =[
        ('No Peel off','NO PEEL OFF'),
        ('No Damage','NO DAMAGE'),
        ('Not Available', 'Not Available')
    ]

    # Fields from FixtureCleaningRecord
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=20, default="QSF-12-15",blank=True)
    month_year = models.DateField(default=timezone.now, blank=True)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    fixture_location = models.CharField(max_length=200, choices=FIXTURE_LOCATION)
    fixture_control_no = models.CharField(max_length=200, choices=CONTROL_NUMBER_CHOICES)
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
        Override save method to generate notifications for cleaning issues.
        Checks multiple conditions and sends structured notifications.
        """
        super().save(*args, **kwargs)
        
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

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

    # Basic information
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01')
    month = models.DateField(default=timezone.now,blank=True)
    date=models.DateField(default=timezone.now,blank=True)
    stage = models.CharField(max_length=200, choices=STATION_CHOICES)
    part_description = models.CharField(max_length=250,choices=STATION_CHOICES)

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

    # # Additional fields for flexibility
    # notes = models.TextField(blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rejection Sheet"
        verbose_name_plural = "Rejection Sheets"
        unique_together = ['month', 'stage', 'part_description']

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
        
        if self.total_pass_qty > metrics['total_input']:
            raise ValidationError({
                "total_pass_qty": (
                    f"Total pass quantity ({self.total_pass_qty}) cannot exceed "
                    f"total input ({metrics['total_input']})"
                )
            })

        if self.closing_balance != metrics['closing_balance']:
            raise ValidationError({
                "closing_balance": (
                    f"Closing balance should be {metrics['closing_balance']} "
                    "(Opening + Rework - Pass - Rejection)"
                )
            })

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
        super().save(*args, **kwargs)
        self.send_notification()

    def __str__(self):
        """String representation of the rejection sheet."""
        return f"Rejection Sheet for {self.part_description} - {self.month.strftime('%B %Y')} ({self.stage})"

# ----------------------------------------------------------------
# SolderingBitRecord
from django.db import models
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

    
class DailyChecklistItem(models.Model):

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None ,blank=True)           
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01',blank=True)
    doc_number = models.CharField(max_length=20, default="QSF-13-06",blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default=timezone.now)
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    month_year = models.DateField(default=timezone.now,blank=True)
    date=models.DateField(default=django.utils.timezone.now,blank=True)
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
    
    check_point_1 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Clean Machine Surface',blank=True)
    check_point_2 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check ON/OFF Switch',blank=True)
    check_point_3 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Emergency Switch',blank=True)
    check_point_4 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check any Abnormal Sound in M/C',blank=True)
    check_point_5 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Spray Nozzle',blank=True)
    check_point_6 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check all Tubbing & Feeder pipe',blank=True)
    check_point_7 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Maintenance & Calibration Tag',blank=True)


    REQUIREMENT_RANGE_CHOICES = (
        ('Proper Clean', 'Proper Clean'),
        ('Proper Working', 'Proper Working'),
        ('Proper Working', 'Proper Working'),
        ('No any Abnormal Sound', 'No any Abnormal Sound'),
        ('No Blockage No leakage', 'No Blockage No leakage'),
        ('No Cut & No Damage', 'No Cut & No Damage'),
        ('No Expiry date on tag', 'No Expiry date on tag'),
    )
    requirement_range_1 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='Proper Clean',blank=True)
    requirement_range_2 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='Proper Working',blank=True)
    requirement_range_3 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='Proper Working',blank=True)
    requirement_range_4 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No any Abnormal Sound',blank=True)
    requirement_range_5 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No Blockage No leakage',blank=True)
    requirement_range_6 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No Cut & No Damage',blank=True)
    requirement_range_7 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No Expiry date on tag',blank=True)
    
    METHOD_OF_CHECKING_CHOICES = (
        ('Clean by Cloths & Brush', 'Clean by Cloths & Brush'),
        ('By Hand', 'By Hand'),
        ('By Eye', 'By Eye'),
        )
    method_of_checking_1 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='Clean by Cloths & Brush',blank=True)
    method_of_checking_2 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Hand',blank=True)
    method_of_checking_3 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Hand',blank=True)
    method_of_checking_4 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Eye',blank=True)
    method_of_checking_5 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Eye',blank=True)
    method_of_checking_6 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Eye',blank=True)
    method_of_checking_7 = models.CharField(max_length=200,choices=METHOD_OF_CHECKING_CHOICES ,default='By Eye',blank=True)
     
 
 
    Remark_1=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_2=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_3=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_4=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_5=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_6=models.CharField(max_length=100,choices=TICK_CHOICES)   
    Remark_7=models.CharField(max_length=100,choices=TICK_CHOICES)   
     
   
    
    checked_by_Operator = models.CharField(max_length=100,choices=TICK_CHOICES,default='✔',blank=True)
    approved_by_Supervisor = models.CharField(max_length=100,choices=TICK_CHOICES,default='✘',blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Maintenance Checklist For Daily"
        verbose_name_plural = "Maintenance Checklists For Daily"

    def __str__(self):
        return f"Daily Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def get_notification_message(self, checkpoint_number, status):
        """
        Generate a notification message that matches the frontend formatting.
        Ensures consistent data structure for proper display.
        """
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
                    'name': getattr(self, f'check_point_{checkpoint_number}') or 'N/A',
                    'requirement': getattr(self, f'requirement_range_{checkpoint_number}') or 'N/A',
                    'method': getattr(self, f'method_of_checking_{checkpoint_number}') or 'N/A',
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
        # Handle manager assignment if available
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        super().save(*args, **kwargs)

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
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None ,blank=True)       
    station = models.CharField(max_length=10, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=20, default="QSF-13-06",blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default=timezone.now)
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    month_year = models.DateField(default=timezone.now,blank=True)
        

    # Weekly Checklist field
    # Choices for check points
    CHECK_POINT_CHOICES = (
        ('Check Conveyor Belts', 'Check Conveyor Belts'),
        ('Check Solder bit Assembly. For any Bolts & Screw Loose', 'Check Solder bit Assembly. For any Bolts & Screw Loose'),
        ('Check Wire & Cable', 'Check Wire & Cable'),
        ('Electrical Insulation', 'Electrical Insulation'),
    )
    date = models.DateField(default=timezone.now,blank=True)
    # Fields for check points with default values
    check_point_8 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Conveyor Belts',blank=True)
    check_point_9 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Solder bit Assembly. For any Bolts & Screw Loose',blank=True)
    check_point_10 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Wire & Cable',blank=True)
    check_point_11 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Electrical Insulation',blank=True)

    # Choices for requirement ranges
    REQUIREMENT_RANGE_CHOICES = (
        ('No Damage', 'No Damage'),
        ('Proper Tight', 'Proper Tight'),
        ('No Damage No Broken', 'No Damage No Broken'),
        ('No Cut & No Damage Wire', 'No Cut & No Damage Wire'),
    )

    # Fields for requirement ranges with default values
    requirement_range_8 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES,  default='No Damage',blank=True)
    requirement_range_9 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES,  default='Proper Tight',blank=True)
    requirement_range_10 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No Damage No Broken',blank=True)
    requirement_range_11 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='No Cut & No Damage Wire',blank=True)

    METHOD_OF_CHECKING_CHOICES = (
        ('Clean by Cloths & Brush', 'Clean by Cloths & Brush'),
        ('By Hand', 'By Hand'),
        ('By Eye', 'By Eye'),
        )
    method_of_checking_8 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Hand',blank=True)
    method_of_checking_9 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Hand',blank=True)
    method_of_checking_10 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Hand',blank=True)
    method_of_checking_11 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Hand',blank=True)


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
        # Handle manager assignment
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        super().save(*args, **kwargs)

        # Send notifications for failed checkpoints
        channel_layer = get_channel_layer()
        
        # Weekly checklist uses checkpoints 8-11
        for checkpoint_number in range(8, 12):
            remark = getattr(self, f'Remark_{checkpoint_number}')
            if remark == '✘':
                notification = self.get_notification_message(checkpoint_number, remark)
                async_to_sync(channel_layer.group_send)('test', notification)

    
class MonthlyChecklistItem(models.Model):


    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]        
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None ,blank=True)    
    station=models.CharField(max_length=200,choices=STATION_CHOICES)
    doc_number = models.CharField(max_length=20, default="QSF-13-06",blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default="2022-12-31")
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    month_year = models.DateField(default=timezone.now)

    CHECK_POINT_CHOICES = (
        ('Check Machine Earthing (Leakage Voltage)', 'Check Machine Earthing (Leakage Voltage)'),        
        ('Check all parameter', 'Check all parameter'),
        ('Check Working condition', 'Check Working condition'),
        ('Check Operation of Sensors', 'Check Operation of Sensors'),
        ('Check condition of all fixture','Check condition of all fixture'),
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
    
    date = models.DateField(default=timezone.now,blank=True)
    # Fields for check points with default values
    check_point_12 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Machine Earthing (Leakage Voltage)',blank=True)
    # Fields for requirement ranges with default values
    requirement_range_12 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='< 2 V',blank=True)

    # Field for method of checking
    method_of_checking_12 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Parameter',blank=True)

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    Remark_12=models.CharField(max_length=100,choices=TICK_CHOICES)
    checked_by_Operator = models.CharField(max_length=100,choices=TICK_CHOICES,default='',blank=True)
    approved_by_Supervisor = models.CharField(max_length=100,choices=TICK_CHOICES ,default='',blank=True)
    history = HistoricalRecords()
    
    
    class Meta:
        verbose_name = "Maintenance Checklist For Monthly"
        verbose_name_plural = "Maintenance Checklists For Monthly"

    def __str__(self):
        return f"Monthly Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def get_checkpoint_details(self, checkpoint_number):
        """
        Retrieve comprehensive checkpoint details.
        Returns formatted checkpoint information with fallback values.
        """
        return {
            'number': checkpoint_number,
            'name': getattr(self, f'check_point_{checkpoint_number}', 'N/A'),
            'requirement': getattr(self, f'requirement_range_{checkpoint_number}', 'N/A'),
            'method': getattr(self, f'method_of_checking_{checkpoint_number}', 'N/A')
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
        # Handle manager assignment if not set
        if not self.manager and hasattr(self, 'request'):
            self.manager = self.request.user

        super().save(*args, **kwargs)

        # Check specifically for checkpoint 12 failure
        channel_layer = get_channel_layer()
        
        if self.Remark_12 == '✘':
            notification = self.get_notification_message(12, self.Remark_12)
            async_to_sync(channel_layer.group_send)('test', notification)






# ----------------------------------------------------------------

from django.db import models
from django.db.models import Avg, StdDev
import math

from django.db import models, IntegrityError

class ControlChartReading(models.Model):
    date = models.DateField(unique=True)
    reading1 = models.FloatField()
    reading2 = models.FloatField()
    reading3 = models.FloatField()
    reading4 = models.FloatField()
    reading5 = models.FloatField()
    usl = models.FloatField(default=375, validators=[MinValueValidator(0)])
    lsl = models.FloatField(default=355, validators=[MinValueValidator(0)])
    history = HistoricalRecords()


    def get_readings(self):
        """Get all readings as a list"""
        return [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
    def check_violations(self, x_bar, r):
        """Check for control chart violations"""
        violations = []
        readings = self.get_readings()
        
        # Check specification limits
        for i, reading in enumerate(readings, 1):
            if reading > self.usl:
                violations.append(f"Reading {i} ({reading:.2f}) exceeds USL ({self.usl})")
            if reading < self.lsl:
                violations.append(f"Reading {i} ({reading:.2f}) below LSL ({self.lsl})")

        # Get control limits from statistics
        control_limits = ControlChartStatistics.calculate_control_limits()
        
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
        capability = ControlChartStatistics.calculate_capability_indices()
        control_limits = ControlChartStatistics.calculate_control_limits()
        
        return {
            'type': 'chat_message',
            'message': {
                'record_id': self.pk,
                'alert_type': 'control_chart_alert',
                'date': self.date.strftime('%Y-%m-%d'),
                'readings': {
                    'values': self.get_readings(),
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
        readings = self.get_readings()
        if any(reading < 0 for reading in readings):
            raise ValidationError("Readings cannot be negative.")
        if self.usl <= self.lsl:
            raise ValidationError("Upper specification limit must be greater than lower specification limit.")

    def _create_or_update_statistics(self):
        readings = [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
        x_bar = sum(readings) / len(readings)
        r = max(readings) - min(readings)

        try:
            stats = ControlChartStatistics.objects.filter(date=self.date).first()
            if stats:
                stats.x_bar = x_bar
                stats.r = r
                stats.usl = self.usl
                stats.lsl = self.lsl
                stats.save()
            else:
                ControlChartStatistics.objects.create(
                    date=self.date,
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
            self.clean()
            super().save(*args, **kwargs)
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
    date = models.DateField(unique=True)
    x_bar = models.FloatField()
    r = models.FloatField()
    usl = models.FloatField(default=375)
    lsl = models.FloatField(default=355)
    history = HistoricalRecords()

    @classmethod
    def get_monthly_statistics(cls):
        try:
            monthly_stats = cls.objects.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                days_count=Count('id'),
                monthly_x_bar=Avg('x_bar'),
                monthly_r=Avg('r'),
                monthly_std_dev=StdDev('x_bar')
            ).order_by('-month')

            processed_stats = []
            for stat in monthly_stats:
                if stat['month']:
                    # Get total calendar days in the month
                    total_days = calendar.monthrange(
                        stat['month'].year,
                        stat['month'].month
                    )[1]
                    
                    monthly_data = {
                        'month': stat['month'],
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
    def calculate_control_limits(cls):
        data = cls.objects.all()
        if not data.exists():
            return {
                'x_bar_avg': 0,
                'r_bar': 0,
                'ucl_x_bar': 0,
                'lcl_x_bar': 0,
                'ucl_r': 0,
                'lcl_r': 0
            }

        x_bar_avg = data.aggregate(Avg('x_bar'))['x_bar__avg']
        r_bar = data.aggregate(Avg('r'))['r__avg']

        # Constants for n=5 subgroup size
        a2, d3, d4 = 0.58, 0, 2.11

        ucl_x_bar = x_bar_avg + a2 * r_bar
        lcl_x_bar = x_bar_avg - a2 * r_bar
        ucl_r = d4 * r_bar
        lcl_r = d3 * r_bar

        return {
            'x_bar_avg': x_bar_avg,
            'r_bar': r_bar,
            'ucl_x_bar': ucl_x_bar,
            'lcl_x_bar': lcl_x_bar,
            'ucl_r': ucl_r,
            'lcl_r': lcl_r
        }

    @classmethod
    def calculate_capability_indices(cls):
        data = cls.objects.all()
        if not data.exists():
            return {
                'cp': 0,
                'cpk': 0,
                'std_dev': 0
            }

        latest_record = data.latest('date')
        x_bar_avg = data.aggregate(Avg('x_bar'))['x_bar__avg']
        std_dev = data.aggregate(StdDev('x_bar'))['x_bar__stddev']

        if std_dev is None or std_dev == 0:
            return {
                'cp': 0,
                'cpk': 0,
                'std_dev': 0
            }

        # Use the specification limits from the latest record
        usl = latest_record.usl
        lsl = latest_record.lsl

        cp = (usl - lsl) / (6 * std_dev)
        cpk = min((usl - x_bar_avg) / (3 * std_dev), (x_bar_avg - lsl) / (3 * std_dev))

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
        violations = []
        
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
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'high'
                })
        
        # Rule C: 6 points in a row, increasing or decreasing
        for i in range(len(data_points) - 5):
            sequence = data_points[i:i+6]
            x_bars = [p['x_bar'] for p in sequence]
            increasing = all(x_bars[j] < x_bars[j+1] for j in range(len(x_bars)-1))
            decreasing = all(x_bars[j] > x_bars[j+1] for j in range(len(x_bars)-1))
            
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
        
        # Rule D: 14 points alternating up and down
        for i in range(len(data_points) - 13):
            sequence = data_points[i:i+14]
            x_bars = [p['x_bar'] for p in sequence]
            alternating = True
            
            for j in range(len(x_bars)-1):
                if j % 2 == 0 and x_bars[j] <= x_bars[j+1]:
                    alternating = False
                    break
                if j % 2 == 1 and x_bars[j] >= x_bars[j+1]:
                    alternating = False
                    break
                    
            if alternating:
                violations.append({
                    'rule': 'D',
                    'index': i,
                    'message': '14 points alternating up and down',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': x_bars,
                    'severity': 'medium'
                })
        
        # Rule E: 2 out of 3 points > 2 standard deviations
        for i in range(len(data_points) - 2):
            sequence = data_points[i:i+3]
            count = sum(1 for p in sequence if is_outside_std_dev(p, 2))
            if count >= 2 and all(is_same_side(p, sequence[0]) for p in sequence):
                violations.append({
                    'rule': 'E',
                    'index': i,
                    'message': '2 out of 3 points > 2 standard deviations from centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'high'
                })
        
        # Rule F: 4 out of 5 points > 1 standard deviation
        for i in range(len(data_points) - 4):
            sequence = data_points[i:i+5]
            count = sum(1 for p in sequence if is_outside_std_dev(p, 1))
            if count >= 4 and all(is_same_side(p, sequence[0]) for p in sequence):
                violations.append({
                    'rule': 'F',
                    'index': i,
                    'message': '4 out of 5 points > 1 standard deviation from centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'medium'
                })
        
        # Rule G: 15 points in a row within 1 standard deviation
        for i in range(len(data_points) - 14):
            sequence = data_points[i:i+15]
            if all(not is_outside_std_dev(p, 1) for p in sequence):
                violations.append({
                    'rule': 'G',
                    'index': i,
                    'message': '15 points in a row within 1 standard deviation of centerline',
                    'date_range': [sequence[0]['date'], sequence[-1]['date']],
                    'points': [p['x_bar'] for p in sequence],
                    'severity': 'medium'
                })
        
        # Rule H: 8 points in a row > 1 standard deviation from centerline
        for i in range(len(data_points) - 7):
            sequence = data_points[i:i+8]
            if all(is_outside_std_dev(p, 1) for p in sequence):
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
    def get_monthly_statistics_with_violations(cls, year, month):
        """
        Get monthly statistics including special cause violations
        """
        monthly_stats = cls.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('date').values('date', 'x_bar', 'r')
        
        if not monthly_stats:
            return [], []
        
        data_points = list(monthly_stats)
        x_bars = [point['x_bar'] for point in data_points]
        mean = sum(x_bars) / len(x_bars)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in x_bars) / len(x_bars))
        
        violations = cls.check_special_causes(data_points, mean, std_dev)
        
        return data_points, violations




# ----------------------------------------------------------------+

class StartUpCheckSheet(models.Model):
    # General Information
    revision_no = models.IntegerField(verbose_name="Rev. No.")
    effective_date = models.DateField(verbose_name="Eff. Date",default=timezone.now, blank=True)
    process_operation = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    month = models.DateField(default=timezone.now, blank=True)
    # Choices for Checkpoints
    OKAY_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
    ]

    # Checkpoints with choices
    checkpoint_1 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 1")
    checkpoint_2 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 2")
    checkpoint_3 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 3")
    checkpoint_4 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 4")
    checkpoint_5 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 5")
    checkpoint_6 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 6")
    checkpoint_7 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 7")
    checkpoint_8 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 8")
    checkpoint_9 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 9")
    checkpoint_10 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 10")
    checkpoint_11 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 11")
    checkpoint_12 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 12")
    checkpoint_13 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 13")
    checkpoint_14 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 14")
    checkpoint_15 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 15")
    checkpoint_16 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 16")
    checkpoint_17 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 17")
    checkpoint_18 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 18")
    checkpoint_19 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 19")
    checkpoint_20 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 20")
    checkpoint_21 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 21")
    checkpoint_22 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 22")
    checkpoint_23 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 23")
    checkpoint_24 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 24")
    checkpoint_25 = models.CharField(max_length=6, choices=OKAY_CHOICES, verbose_name="Check Point 25")
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=None ,blank=True)    
    # defects = models.TextField(blank=True)
    verified_by = models.CharField(max_length=1, choices=OKAY_CHOICES, default='✘',blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Start Up Check Sheet"
        verbose_name_plural = "Start Up Check Sheets"


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
                'process_operation': str(self.process_operation) or 'Not Specified',
                'effective_date': self.effective_date.strftime('%Y-%m-%d'),
                
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
                'month': self.month.strftime('%B %Y'),
                
                # Additional context
                'shift': getattr(self, 'shift', 'Not Specified'),
                'department': str(getattr(self, 'department', 'Not Specified'))
            }
        }

    def save(self, *args, **kwargs):
            if not self.manager and hasattr(self, 'request'):
                self.manager = self.request.user

            super().save(*args, **kwargs)

            # Check for 'Not OK' checkpoints and send structured notifications
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
    def __str__(self):
            return f"Start Up Check Sheet {self.revision_no} - {self.effective_date.strftime('%Y-%m-%d')}"





# ---------------------------------------------------------------------

from django.db import models
from django.utils import timezone
from django.db.models import Avg, Sum, F, ExpressionWrapper, StdDev, Variance
from django.db.models.functions import Sqrt
import math

class PChartData(models.Model):
    # Required input fields
    location = models.CharField(max_length=200, choices=MACHINE_LOCATION_CHOICES)
    part_number_and_name = models.CharField(max_length=200)
    operation_number_and_stage_name = models.CharField(max_length=200, choices=STATION_CHOICES)
    department = models.CharField(max_length=100)
    month = models.DateField(default=timezone.now)
    date_control_limits_calculated = models.DateField(default=timezone.now)
    average_sample_size = models.IntegerField()
    frequency = models.IntegerField()
    sample_size = models.IntegerField()
    nonconforming_units = models.IntegerField()
    history = HistoricalRecords()

    # Automatically calculated fields
    proportion = models.FloatField(null=True, blank=True)
    ucl_p = models.FloatField(null=True, blank=True)
    lcl_p = models.FloatField(null=True, blank=True)
    ucl_np = models.FloatField(null=True, blank=True)
    lcl_np = models.FloatField(null=True, blank=True)
    ucl_c = models.FloatField(null=True, blank=True)
    lcl_c = models.FloatField(null=True, blank=True)
    ucl_u = models.FloatField(null=True, blank=True)
    lcl_u = models.FloatField(null=True, blank=True)

    def calculate_control_limits(self):
        try:
            # Calculate proportion
            self.proportion = self.nonconforming_units / self.sample_size if self.sample_size > 0 else None
            
            # P-Chart limits
            if self.average_sample_size > 0 and self.proportion and 0 < self.proportion < 1:
                p_std = math.sqrt((self.proportion * (1 - self.proportion)) / self.average_sample_size)
                self.ucl_p = min(1, self.proportion + 3 * p_std)
                self.lcl_p = max(0, self.proportion - 3 * p_std)
            
            # NP-Chart limits
            if self.proportion is not None:
                np_bar = self.average_sample_size * self.proportion
                if np_bar > 0:
                    np_std = math.sqrt(np_bar * (1 - self.proportion))
                    self.ucl_np = np_bar + 3 * np_std
                    self.lcl_np = max(0, np_bar - 3 * np_std)
            
            # C-Chart limits
            if self.nonconforming_units > 0:
                c_std = math.sqrt(self.nonconforming_units)
                self.ucl_c = self.nonconforming_units + 3 * c_std
                self.lcl_c = max(0, self.nonconforming_units - 3 * c_std)
            
            # U-Chart limits
            if self.average_sample_size > 0:
                u_bar = self.nonconforming_units / self.average_sample_size
                if u_bar > 0:
                    u_std = math.sqrt(u_bar / self.average_sample_size)
                    self.ucl_u = u_bar + 3 * u_std
                    self.lcl_u = max(0, u_bar - 3 * u_std)

        except (ZeroDivisionError, ValueError) as e:
            print(f"Error calculating control limits: {e}")

    def check_control_limits(self):
        """Check for out-of-control conditions"""
        violations = []
        
        if self.proportion is not None:
            # P-Chart violations
            if self.ucl_p is not None and self.proportion > self.ucl_p:
                violations.append(f"P-Chart: Proportion ({self.proportion:.4f}) exceeds UCL ({self.ucl_p:.4f})")
            if self.lcl_p is not None and self.proportion < self.lcl_p:
                violations.append(f"P-Chart: Proportion ({self.proportion:.4f}) below LCL ({self.lcl_p:.4f})")

            # NP-Chart violations
            np_value = self.average_sample_size * self.proportion
            if self.ucl_np is not None and np_value > self.ucl_np:
                violations.append(f"NP-Chart: Value ({np_value:.4f}) exceeds UCL ({self.ucl_np:.4f})")
            if self.lcl_np is not None and np_value < self.lcl_np:
                violations.append(f"NP-Chart: Value ({np_value:.4f}) below LCL ({self.lcl_np:.4f})")

        # U-Chart violations
        if self.average_sample_size > 0:
            u_value = self.nonconforming_units / self.average_sample_size
            if self.ucl_u is not None and u_value > self.ucl_u:
                violations.append(f"U-Chart: Rate ({u_value:.4f}) exceeds UCL ({self.ucl_u:.4f})")
            if self.lcl_u is not None and u_value < self.lcl_u:
                violations.append(f"U-Chart: Rate ({u_value:.4f}) below LCL ({self.lcl_u:.4f})")

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
                'date': self.month.strftime('%Y-%m-%d'),
                'metrics': {
                    'sample_size': self.sample_size,
                    'nonconforming': self.nonconforming_units,
                    'proportion': round(self.proportion, 4) if self.proportion else None,
                    'average_sample_size': self.average_sample_size
                },
                'control_limits': {
                    'p_chart': {
                        'ucl': round(self.ucl_p, 4) if self.ucl_p else None,
                        'lcl': round(self.lcl_p, 4) if self.lcl_p else None
                    },
                    'np_chart': {
                        'ucl': round(self.ucl_np, 4) if self.ucl_np else None,
                        'lcl': round(self.lcl_np, 4) if self.lcl_np else None
                    },
                    'u_chart': {
                        'ucl': round(self.ucl_u, 4) if self.ucl_u else None,
                        'lcl': round(self.lcl_u, 4) if self.lcl_u else None
                    }
                },
                'violations': violations,
                'needs_attention': bool(violations),
                'severity': 'high' if len(violations) > 1 else 'medium' if violations else 'low'
            }
        }

    def save(self, *args, **kwargs):
        # Calculate control limits (your existing method)
        self.calculate_control_limits()
        
        # Save the record
        super().save(*args, **kwargs)
        
        # Check for violations and send notification
        violations = self.check_control_limits()
        if violations:
            channel_layer = get_channel_layer()
            notification = self.get_notification_message(violations)
            async_to_sync(channel_layer.group_send)('test', notification)
