from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    my_skill = models.IntegerField(default=0, blank=True)
    matrix = models.CharField(max_length=400, blank=True, null=True)
    Image = models.ImageField(upload_to='profile_picture/', blank=True, null=True)    
    

    def __str__(self):
        return self.user.username

# Signal to create profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
                  
# Signal to save profile whenever user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)