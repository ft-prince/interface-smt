# machineapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import MachineLoginForm
from .models import Machine, MachineLoginStatus,MachineLoginTracker
from user_app.models import Profile
import uuid
from django.http import JsonResponse
import json

def generate_device_id(request):
    # Generate a device ID if not exists
    if 'machine_device_id' not in request.session:
        request.session['machine_device_id'] = str(uuid.uuid4())
    return request.session['machine_device_id']

def home(request):
    browser_key = request.session.get('browser_key')
    active_machine = None
    
    if browser_key:
        machine_status = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).first()
        if machine_status:
            active_machine = machine_status.machine
    
    context = {
        'machine': active_machine,
    }
    
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
        context['user_profile'] = user_profile
        
        if active_machine:
            has_required_skills = user_profile.my_skill >= active_machine.required_skills
            is_authorized = active_machine.users.filter(id=request.user.id).exists()
            
            if has_required_skills and is_authorized:
                return render(request, 'core/home_user_machine.html', context)
            else:
                if not has_required_skills:
                    messages.error(request, "Insufficient skills. You will be logged out in 10 seconds.")
                if not is_authorized:
                    messages.error(request, f"You are not authorized to use {active_machine.name}. Please contact your administrator for access. You will be logged out in 10 seconds.")
                logout(request)
                return render(request, 'core/skill_error.html', context)
        
        return render(request, 'core/home_user.html', context)
    
    if active_machine:
        return render(request, 'core/home_machine.html', context)
    return render(request, 'core/home.html', context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'core/user_login.html')


def machine_login(request):
    if request.method == 'POST':
        form = MachineLoginForm(request.POST)
        if form.is_valid():
            machine = form.cleaned_data['machine']
            
            # Generate a browser key if not present
            browser_key = request.session.get('browser_key')
            if not browser_key:
                browser_key = str(uuid.uuid4())
                request.session['browser_key'] = browser_key
            
            # Create machine login record
            MachineLoginTracker.objects.create(
                machine=machine,
                browser_key=browser_key
            )
            return redirect('home')
    else:
        form = MachineLoginForm()
    return render(request, 'core/machine_login.html', {'form': form})




def user_logout(request):
    logout(request)
    return redirect('home')

def skill_based_user_logout(request):
    logout(request)
    messages.info(request, "You've been logged out due to insufficient skills.")
    return redirect('home')


def machine_logout(request):
    browser_key = request.session.get('browser_key')
    if browser_key:
        MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).update(is_active=False)
    return redirect('home')


def check_machine_status(request):
    browser_key = request.GET.get('browser_key')
    active_machine = MachineLoginTracker.objects.filter(
        browser_key=browser_key,
        is_active=True
    ).first()
    
    return JsonResponse({
        'is_active': bool(active_machine),
        'machine_name': active_machine.machine.name if active_machine else None
    })

