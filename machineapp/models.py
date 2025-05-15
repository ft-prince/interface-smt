# machineapp/models.py
from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    name = models.CharField(max_length=100)
    required_skills = models.IntegerField(default=0)
    users = models.ManyToManyField(User, related_name='machines', blank=True)
    # New fields for checklist associations
    show_fixture_cleaning = models.BooleanField(default=True)
    show_rejection_sheets = models.BooleanField(default=True)
    show_soldering_bit = models.BooleanField(default=True)
    show_maintenance_checklist = models.BooleanField(default=True)
    show_reading_list = models.BooleanField(default=True)
    show_pchart = models.BooleanField(default=True)
    show_startup_checklist = models.BooleanField(default=True)
    # New field for tip voltage and resistance record
    show_tip_voltage_resistance = models.BooleanField(default=True)
    # New fields for other sheets
    show_pcb_panel_inspection = models.BooleanField(default=True)
    show_rework_analysis = models.BooleanField(default=True)
    show_solder_paste_control = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MachineLoginStatus(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='login_status')
    device_id = models.CharField(max_length=100)  # Unique identifier for each device/browser
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('machine', 'device_id')

    def __str__(self):
        return f"{self.machine.name} - {self.device_id}"
    
    
    
class MachineLoginTracker(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    browser_key = models.CharField(max_length=100)  # Stored in localStorage instead of session
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.machine.name} - {self.browser_key[:8]}... - {'Active' if self.is_active else 'Inactive'}"
