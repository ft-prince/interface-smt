from django.db import models




class Machine(models.Model):
    name = models.CharField(max_length=100)
    required_skills = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False,blank=True)

    def __str__(self):
        return self.name
    

class ActiveMachine(models.Model):
    machine = models.OneToOneField('Machine', on_delete=models.CASCADE)
    activated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Active: {self.machine.name}"    