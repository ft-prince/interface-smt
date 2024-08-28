from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    my_skill = models.IntegerField(default=0,blank=True)  # You can set a default value

    def __str__(self):
        return self.user.username
