from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    my_skill = models.IntegerField(default=0,blank=True) # set a default value
    user_Id=models.CharField(max_length=200,blank=True)
    matrix=models.CharField(max_length=400,blank=True,null=True)

    def __str__(self):
        return self.user.username

