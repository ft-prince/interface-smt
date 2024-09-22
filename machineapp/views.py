# machineapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import MachineLoginForm
from .models import Machine
from user_app.models import Profile

def home(request):
    active_machine = Machine.objects.filter(is_active=True).first()
    
    context = {
        'machine': active_machine,
    }
    
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
        context['user_profile'] = user_profile
        
        if active_machine:
            if user_profile.my_skill >= active_machine.required_skills:
                return render(request, 'core/home_user_machine.html', context)
            else:
                messages.error(request, "Insufficient skills. You will be logged out in 10 seconds.")
                return render(request, 'core/skill_error.html', context)
        else:
            return render(request, 'core/home_user.html', context)
    else:
        if active_machine:
            return render(request, 'core/home_machine.html', context)
        else:
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

def user_logout(request):
    logout(request)
    return redirect('home')

def machine_login(request):
    if request.method == 'POST':
        form = MachineLoginForm(request.POST)
        if form.is_valid():
            machine = form.cleaned_data['machine']
            # Deactivate any currently active machine
            Machine.objects.filter(is_active=True).update(is_active=False)
            # Activate the selected machine
            machine.is_active = True
            machine.save()
            return redirect('home')
    else:
        form = MachineLoginForm()
    return render(request, 'core/machine_login.html', {'form': form})

def machine_logout(request):
    Machine.objects.filter(is_active=True).update(is_active=False)
    return redirect('home')

def skill_based_user_logout(request):
    logout(request)
    messages.info(request, "You've been logged out due to insufficient skills.")
    return redirect('home')