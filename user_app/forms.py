from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserForm(UserCreationForm):
    email = forms.EmailField() # required is default otherwise mention required=False
    class Meta:
        model = User
        fields = ['username','email','password1','password2']