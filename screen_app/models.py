#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import django

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

    # Fields from FixtureCleaningRecord
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=20, default="QSF-12-15",blank=True)
    month_year = models.DateField()
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    fixture_location = models.CharField(max_length=200, choices=FIXTURE_LOCATION)
    fixture_control_no = models.CharField(max_length=200, choices=CONTROL_NUMBER_CHOICES)
    fixture_installation_date = models.DateField()
    # Fields from DailyRecord
    date = models.DateField(default=timezone.now,blank=True)
    time = models.TimeField(default=timezone.now,blank=True)
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    verification_tag_available = models.CharField(max_length=25, choices=TAG_CHOICES)
    verification_tag_condition = models.CharField(max_length=25, choices=TAG_CHOICES)
    no_dust_on_fixture = models.CharField(max_length=25, choices=TAG_CHOICES)
    no_epoxy_coating_on_fixture = models.CharField(max_length=25, choices=TAG_CHOICES)
    operator_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✔',blank=True)
    supervisor_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✘',blank=True)

    class Meta:
        verbose_name = "Fixture Cleaning Record"
        verbose_name_plural = "Fixture Cleaning Records"

    def save(self, *args, **kwargs):
        # Call the parent save method
        super().save(*args, **kwargs)

        # Send notifications if any field is 'Not Available'
        channel_layer = get_channel_layer()
        if self.verification_tag_available == 'Not Available':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Fixture Cleaning Record {self.pk}: Verification Tag Available is Not Available'
                }
            )
        if self.verification_tag_condition == 'Not Available':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Fixture Cleaning Record {self.pk}: Verification Tag Condition is Not Available'
                }
            )
        if self.no_dust_on_fixture == 'Not Available':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Fixture Cleaning Record {self.pk}: No Dust on Fixture is Not Available'
                }
            )
        if self.no_epoxy_coating_on_fixture == 'Not Available':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Fixture Cleaning Record {self.pk}: No Epoxy Coating on Fixture is Not Available'
                }
            )

    def __str__(self):
        return f"Cleaning Record {self.fixture_control_no} - {self.date}"

# ----------------------------------------------------------------
# Rejection sheet

from django.core.validators import MinValueValidator
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

    # # Additional fields for flexibility
    # notes = models.TextField(blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rejection Sheet"
        verbose_name_plural = "Rejection Sheets"
        unique_together = ['month', 'stage', 'part_description']

    def __str__(self):
        return f"Rejection Sheet for {self.part_description} - {self.month.strftime('%B %Y')} ({self.stage})"
        
    def calculate_total_pass_qty(self):
        return self.opening_balance + self.receive_from_rework

    def save(self, *args, **kwargs):
        # Automatically calculate total_pass_qty
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user        
        self.total_pass_qty = self.calculate_total_pass_qty()
        super().save(*args, **kwargs)

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

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked'),
    ]

    station = models.CharField(max_length=100, default='DSL01_S01')
    doc_number = models.CharField(max_length=50, verbose_name="Doc. No.", default='Doc-QSF-12-15', blank=True)
    part_name = models.CharField(max_length=100, choices=PART_CHOICES)
    machine_no = models.ForeignKey(MachineLocation, on_delete=models.CASCADE, verbose_name="Process/Operation")
    machine_location = models.CharField(max_length=150,choices=LOCATION_CHOICES)
    month = models.DateField(default=timezone.now, blank=True)
    time = models.TimeField(default=timezone.now, blank=True)
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    soldering_points_per_part = models.IntegerField(default=10)
    bit_size = models.CharField(max_length=20, default="20DV")
    date = models.DateField(default=timezone.now, blank=True)
    produce_quantity_shift_a = models.IntegerField(verbose_name="Produce Quantity Shift A")
    produce_quantity_shift_b = models.IntegerField(verbose_name="Produce Quantity Shift B")
    total_quantity = models.IntegerField(verbose_name="Total Quantity (Both shifts)", default=500)
    total_soldering_points = models.IntegerField(verbose_name="Total Soldering points/day", default=500)
    bit_life_remaining = models.IntegerField(verbose_name="Bit Life Remaining (Parts in Nos.)", default=500)
    bit_change_date = models.DateField(verbose_name="Bit Change Date")
    prepared_by = models.CharField(max_length=100, choices=TICK_CHOICES, blank=True)
    approved_by = models.CharField(max_length=100, choices=TICK_CHOICES, blank=True)

    class Meta:
        verbose_name = "Robotic Soldering Bit Replacement Record"
        verbose_name_plural = "Robotic Soldering Bit Replacement Records"

    def __str__(self):
        return f"Record {self.doc_number} - {self.date}"

    def send_notification(self, message):
        # Sending notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "test",  # the name of the group to send the message to
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def save(self, *args, **kwargs):
        # Calculate total quantity and total soldering points
        self.total_quantity = self.produce_quantity_shift_a + self.produce_quantity_shift_b
        self.total_soldering_points = self.total_quantity * self.soldering_points_per_part
        # Calculate bit life remaining
        self.bit_life_remaining = 12000 - self.total_quantity

        # Notification logic for WebSocket
        if self.prepared_by == '✘' or self.approved_by == '✘':
            message = f"Record {self.doc_number} marked as 'Not OK'."
            self.send_notification(message)

        super().save(*args, **kwargs)


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
    
    class Meta:
        verbose_name = "Maintenance Checklist For Daily "
        verbose_name_plural = "Maintenance Checklists For Daily"

    def __str__(self):
        return f"Daily Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    def save(self, *args, **kwargs):
        # Call the parent save method
        super().save(*args, **kwargs)

        # Check for 'Not OK' remarks and send notifications
        channel_layer = get_channel_layer()
        if self.Remark_1 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 1 is Not OK'
                }
            )
        if self.Remark_2 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 2 is Not OK'
                }
            )
        if self.Remark_3 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 3 is Not OK'
                }
            )
        if self.Remark_4 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 4 is Not OK'
                }
            )
        if self.Remark_5 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 5 is Not OK'
                }
            )
        if self.Remark_6 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 6 is Not OK'
                }
            )
        if self.Remark_7 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Daily Checklist Item {self.pk}: Remark 7 is Not OK'
                }
            )


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

    
    
    def save(self, *args, **kwargs):
        # Call the parent save method
        super().save(*args, **kwargs)

        # Check for 'Not OK' remarks and send notifications
        channel_layer = get_channel_layer()
        if self.Remark_8 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Weekly Checklist Item {self.pk}: Remark 8 is Not OK'
                }
            )
        if self.Remark_9 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Weekly Checklist Item {self.pk}: Remark 9 is Not OK'
                }
            )
        if self.Remark_10 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Weekly Checklist Item {self.pk}: Remark 10 is Not OK'
                }
            )
        if self.Remark_11 == '✘':
            async_to_sync(channel_layer.group_send)(
                'test',
                {
                    'type': 'chat_message',
                    'message': f'Weekly Checklist Item {self.pk}: Remark 11 is Not OK'
                }
            )

    
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
    
    
    def __str__(self):
        return f"MonthlyChecklistItem: {self.pk}"

    def save(self, *args, **kwargs):
        # Check if Remark_12 is set to "Not OK"
        if self.Remark_12 == '✘':
            # Trigger WebSocket notification
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'test',  # Use the same group name as in the WebSocket consumer
                {
                    'type': 'chat_message',
                    'message': f'Notification: Remark 12 is Not OK for MonthlyChecklistItem {self.pk}'
                }
            )
        
        super().save(*args, **kwargs)







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

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.calculate_statistics()

    def clean(self):
        readings = [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
        if any(reading < 0 for reading in readings):  # Example validation
            raise ValueError("Readings cannot be negative.")

    def calculate_statistics(self):
        readings = [self.reading1, self.reading2, self.reading3, self.reading4, self.reading5]
        x_bar = sum(readings) / len(readings)
        r = max(readings) - min(readings)

        try:
            stats, created = ControlChartStatistics.objects.get_or_create(date=self.date)
            stats.x_bar = x_bar
            stats.r = r
            stats.save()
        except IntegrityError:
            print("IntegrityError occurred while saving statistics.")


import math
from django.db import models
from django.db.models import Avg, StdDev

class ControlChartStatistics(models.Model):
    date = models.DateField(unique=True)
    x_bar = models.FloatField()
    r = models.FloatField()

    @classmethod
    def calculate_control_limits(cls):
        data = cls.objects.all()
        if not data.exists():
            return None  # Handle cases where no data exists

        x_bar_avg = data.aggregate(Avg('x_bar'))['x_bar__avg']
        r_bar = data.aggregate(Avg('r'))['r__avg']

        a2, d3, d4 = 0.58, 0, 2.11  # Constants for n=5 from the chart

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
    def calculate_capability_indices(cls, usl, lsl):
        data = cls.objects.all()
        if not data.exists():
            return None  # Handle cases where no data exists

        x_bar_avg = data.aggregate(Avg('x_bar'))['x_bar__avg']
        std_dev = data.aggregate(StdDev('x_bar'))['x_bar__stddev']

        if std_dev is None or std_dev == 0:
            std_dev = 1  # Avoid division by zero

        cp = (usl - lsl) / (6 * std_dev)
        cpk = min((usl - x_bar_avg) / (3 * std_dev), (x_bar_avg - lsl) / (3 * std_dev))

        return {
            'cp': cp,
            'cpk': cpk,
            'std_dev': std_dev
        }



# > python -m pip uninstall channels
# > python -m pip install -Iv channels==3.0.5




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

    class Meta:
        verbose_name = "Start Up Check Sheet"
        verbose_name_plural = "Start Up Check Sheets"

    def save(self, *args, **kwargs):
        # Call the parent save method
        super().save(*args, **kwargs)

        # Send notifications if any checkpoint is 'Not OK'
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
            if checkpoint == '✘':  # 'Not OK'
                async_to_sync(channel_layer.group_send)(
                    'test',
                    {
                        'type': 'chat_message',
                        'message': f'StartUp Check Sheet Record {self.pk}: Check Point {i} is Not OK'
                    }
                )

    def __str__(self):
        return f"Start Up Check Sheet {self.revision_no} - {self.effective_date.strftime('%Y-%m-%d')}"

