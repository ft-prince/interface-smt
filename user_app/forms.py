from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

class CustomUserForm(UserCreationForm):
    email = forms.EmailField() # required is default otherwise mention required=False
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        

class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label="Select User")

    class Meta:
        model = Profile
        fields = ['user', 'my_skill','matrix']
 