from django.shortcuts import render, redirect
from user_app.forms import CustomUserForm
from django.http import HttpResponse
from django.contrib import messages


from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def register(request):
    if request.method == 'POST':
        register_form = CustomUserForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)  # Log in the user after registration
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')  # Redirect to the login page
    else:
        register_form = CustomUserForm()
    return render(request, 'register.html', {'register_form': register_form})
