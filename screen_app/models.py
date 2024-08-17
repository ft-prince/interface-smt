#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import django

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
    CONTROL_NO = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]

    FIXTURE_LOCATION = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]
    
    TAG_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    CHECK_CHOICES = [
        ('OK', 'OK'),
        ('NG', 'NG'),
    ]
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

    # Fields from FixtureCleaningRecord
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=20, default="QSF-12-15",blank=True)
    month_year = models.DateField()
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    fixture_location = models.CharField(max_length=10, choices=FIXTURE_LOCATION)
    fixture_control_no = models.CharField(max_length=200, choices=CONTROL_NO)
    fixture_installation_date = models.DateField()
    # Fields from DailyRecord
    date = models.DateField(default=timezone.now,blank=True)
    time = models.TimeField(default=timezone.now,blank=True)
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    verification_tag_available = models.CharField(max_length=13, choices=TAG_CHOICES)
    verification_tag_condition = models.CharField(max_length=2, choices=CHECK_CHOICES)
    no_dust_on_fixture = models.CharField(max_length=2, choices=CHECK_CHOICES)
    no_epoxy_coating_on_fixture = models.CharField(max_length=2, choices=CHECK_CHOICES)
    operator_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✔',blank=True)
    supervisor_signature = models.CharField(max_length=1, choices=TICK_CHOICES, default='✘',blank=True)

    class Meta:
        verbose_name = "Fixture Cleaning Record"
        verbose_name_plural = "Fixture Cleaning Records"

    def save(self, *args, **kwargs):
        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user
        super().save(*args, **kwargs)

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
    stage = models.CharField(max_length=7, choices=STAGE_CHOICES)
    part_description = models.CharField(max_length=15,choices=STAGE_CHOICES)

    # Quantity fields
    opening_balance = models.IntegerField(validators=[MinValueValidator(0)])
    receive_from_rework = models.IntegerField(validators=[MinValueValidator(0)])
    total_pass_qty = models.IntegerField(validators=[MinValueValidator(0)])
    total_rejection_qty = models.IntegerField(validators=[MinValueValidator(0)])
    closing_balance = models.IntegerField(validators=[MinValueValidator(0)])
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

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
class SolderingBitRecord(models.Model):

    PART_CHOICES = (
    ('Part 1', 'Part 1 Description'),
    ('Part 2', 'Part 2 Description'),
    ('Part 3', 'Part 3 Description'),
     )      

    MACHINE_CHOICES = (
        ('M1', 'Machine 1'),
        ('M2', 'Machine 2'),
        ('M3', 'Machine 3'),
        # Add more as needed
    )
    LOCATION_CHOICES = (
        ('Location A', 'Location A'),
        ('Location B', 'Location B'),
        ('Location C', 'Location C'),
        # Add more as needed
    )
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=50, verbose_name="Doc. No.",default='Doc-QSF-12-15',blank=True)
    part_name = models.CharField(max_length=100, choices=PART_CHOICES)
    machine_no = models.CharField(max_length=150,choices=MACHINE_CHOICES)
    machine_location = models.CharField(max_length=150,choices=STATION_CHOICES)
    month = models.DateField(default=timezone.now,blank=True)
    time = models.TimeField(default=timezone.now,blank=True)
    operator_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    soldering_points_per_part = models.IntegerField(default=10)
    bit_size = models.CharField(max_length=20, default="20DV")
# ----------------------------------------------------------------------------
    date = models.DateField(default=timezone.now,blank=True)
    produce_quantity_shift_a = models.IntegerField(verbose_name="Produce Quantity Shift A")
    produce_quantity_shift_b = models.IntegerField(verbose_name="Produce Quantity Shift B")
    total_quantity = models.IntegerField(verbose_name="Total Quantity (Both shift)",default=500,help_text="This field is automatically calculated based on the sum of produce_quantity_shift_a and produce_quantity_shift_b."
)
    total_soldering_points = models.IntegerField(verbose_name="Total Soldering points/day",default=500,help_text="This field is automatically calculated based on the total quantity and soldering points per part.",blank=True
)
    bit_life_remaining = models.IntegerField(verbose_name="Bit Life Remaining (Parts in Nos.)",default=500,help_text="This field is automatically calculated based on the total quantity and the initial bit life.",blank=True
)
    bit_change_date = models.DateField(verbose_name="Bit Change Date")
    
    
    prepared_by = models.CharField(max_length=100,choices=TICK_CHOICES,blank=True)
    approved_by = models.CharField(max_length=100,choices=TICK_CHOICES,blank=True)

    class Meta:
        verbose_name = "Robotic Soldering Bit Replacement Record"
        verbose_name_plural = "Robotic Soldering Bit Replacement Records"

    def __str__(self):
        return f"Record {self.doc_number} - {self.date}"

    def save(self, *args, **kwargs):
        # Calculate total quantity and total soldering points
        self.total_quantity = self.produce_quantity_shift_a + self.produce_quantity_shift_b
        self.total_soldering_points = self.total_quantity * self.soldering_points_per_part
        # Calculate bit life remaining
        self.bit_life_remaining = 12000 - self.total_quantity

        if not self.operator_name and hasattr(self, 'request'):
            self.operator_name = self.request.user
        
        super().save(*args, **kwargs)



# ----------------------------------------------------------------

    
class DailyChecklistItem(models.Model):
    MACHINE_NAME_CHOICES = (
        ('Machine 1', 'Machine 1'),
        ('Machine 2', 'Machine 2'),
        ('Machine 3', 'Machine 3'),
        # Add more machines as needed
    )
    CONTROL_NUMBER_CHOICES = (
        ('Control A', 'Control A'),
        ('Control B', 'Control B'),
        ('Control C', 'Control C'),
        # Add more controls as needed
    )
    MACHINE_LOCATION_CHOICES = (
        ('Location A', 'Location A'),
        ('Location B', 'Location B'),
        ('Location C', 'Location C'),
        # Add more locations as needed
    )
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

        
    station = models.CharField(max_length=100, choices=STATION_CHOICES, default='DSL01_S01',blank=True)
    doc_number = models.CharField(max_length=20, default="QSF-13-06",blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default=timezone.now)
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.CharField(max_length=100,choices=MACHINE_LOCATION_CHOICES)
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
        return f" Daily Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"


class WeeklyChecklistItem(models.Model):
    MACHINE_NAME_CHOICES = (
        ('Machine 1', 'Machine 1'),
        ('Machine 2', 'Machine 2'),
        ('Machine 3', 'Machine 3'),
        # Add more machines as needed
    )
    CONTROL_NUMBER_CHOICES = (
        ('Control A', 'Control A'),
        ('Control B', 'Control B'),
        ('Control C', 'Control C'),
        # Add more controls as needed
    )
    MACHINE_LOCATION_CHOICES = (
        ('Location A', 'Location A'),
        ('Location B', 'Location B'),
        ('Location C', 'Location C'),
        # Add more locations as needed
    )
    CHECKLIST_TYPE_CHOICES = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    )
    
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    station = models.CharField(max_length=10, choices=STATION_CHOICES, default='DSL01_S01')
    doc_number = models.CharField(max_length=20, default="QSF-13-06",blank=True)
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default=timezone.now)
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.CharField(max_length=100,choices=MACHINE_LOCATION_CHOICES)
    month_year = models.DateField(default=timezone.now,blank=True)
        

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
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

    
    
    class Meta:
        verbose_name = "Maintenance Checklist for Weekly Basis"
        verbose_name_plural = "Maintenance Checklists for Weekly Basis"

    def __str__(self):
        return f"Checklist for {self.machine_name} - {self.month_year.strftime('%B %Y')}"

    
class MonthlyChecklistItem(models.Model):
    MACHINE_NAME_CHOICES = (
        ('Machine 1', 'Machine 1'),
        ('Machine 2', 'Machine 2'),
        ('Machine 3', 'Machine 3'),
        # Add more machines as needed
    )
    CONTROL_NUMBER_CHOICES = (
        ('Control A', 'Control A'),
        ('Control B', 'Control B'),
        ('Control C', 'Control C'),
        # Add more controls as needed
    )
    MACHINE_LOCATION_CHOICES = (
        ('Location A', 'Location A'),
        ('Location B', 'Location B'),
        ('Location C', 'Location C'),
        # Add more locations as needed
    )
    CHECKLIST_TYPE_CHOICES = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    )
    
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

        
    station=models.ForeignKey(Screen, on_delete=models.CASCADE, default=None)
    doc_number = models.CharField(max_length=20, default="QSF-13-06")
    rev_number = models.CharField(max_length=10, default="02")
    rev_date = models.DateField(default="2022-12-31")
    machine_name = models.CharField(max_length=100, choices=MACHINE_NAME_CHOICES)
    control_number = models.CharField(max_length=100,choices=CONTROL_NUMBER_CHOICES)
    machine_location = models.CharField(max_length=100,choices=MACHINE_LOCATION_CHOICES)
    month_year = models.DateField(default=timezone.now)
    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]

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
    
    date = models.DateField(default=timezone.now,blank=True)
    # Fields for check points with default values
    check_point_12 = models.CharField(max_length=200, choices=CHECK_POINT_CHOICES, default='Check Machine Earthing (Leakage Voltage)')
    # Fields for requirement ranges with default values
    requirement_range_12 = models.CharField(max_length=200, choices=REQUIREMENT_RANGE_CHOICES, default='< 2 V')

    # Field for method of checking
    method_of_checking_12 = models.CharField(max_length=200, choices=METHOD_OF_CHECKING_CHOICES, default='By Parameter')

    TICK_CHOICES = [
        ('✔', 'OK'),
        ('✘', 'Not OK'),
        ('', 'Not Checked')
    ]
    Remark_12=models.CharField(max_length=100,choices=TICK_CHOICES)

    checked_by_Operator = models.CharField(max_length=100,choices=TICK_CHOICES,default='')
    approved_by_Supervisor = models.CharField(max_length=100,choices=TICK_CHOICES ,default='',blank=True)
    
    
    def __str__(self):
        return f"MonthlyChecklistItem: {self.pk}"







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
