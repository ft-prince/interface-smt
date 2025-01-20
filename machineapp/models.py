# machineapp/models.py
from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    name = models.CharField(max_length=100)
    required_skills = models.IntegerField(default=0)
    users = models.ManyToManyField(User, related_name='machines', blank=True)

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

    class Meta:
        unique_together = ('machine', 'browser_key')    