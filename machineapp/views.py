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

# Update the home view in machineapp/views.py

def home(request):
    """Main home view that handles both machine and user authentication"""
    browser_key = request.session.get('browser_key')
    active_machine = None
    active_machines = []
    
    if browser_key:
        # Get all active machine logins for this browser
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if machine_statuses:
            # Get the most recently accessed machine as the active one
            active_machine = machine_statuses.order_by('-created_at').first().machine
            # Get all active machines for the dropdown
            active_machines = [status.machine for status in machine_statuses]
    
    # For debugging
    print(f"Browser key: {browser_key}")
    print(f"Active machine: {active_machine.name if active_machine else 'None'}")
    print(f"Active machines count: {len(active_machines)}")
    
    context = {
        'active_machine': active_machine,
        'active_machines': active_machines,
        'has_browser_key': bool(browser_key),  # Add this for debugging in template

    }
    
    if request.user.is_authenticated:
        # Check if user is admin and redirect to dashboard
        if request.user.is_superuser:
            return redirect('screen/dashboard')
            
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


def switch_machine(request, machine_id):
    """View for switching to a different machine that the user has already logged into"""
    browser_key = request.session.get('browser_key')
    
    if browser_key:
        # Find all active machines for this browser
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        )
        
        # Check if the requested machine is one of the active machines
        requested_machine_status = machine_statuses.filter(machine_id=machine_id).first()
        
        if requested_machine_status:
            # Update the accessed time to make this the most recently accessed machine
            requested_machine_status.save()  # This updates the auto_now fields
            
            messages.success(request, f"Switched to {requested_machine_status.machine.name}")
    
    return redirect('home')

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
            
            # Add debug message
            print(f"Machine login attempt - Machine: {machine.name}, Browser Key: {browser_key}")
            
            try:
                # Check if an active login already exists
                existing_tracker = MachineLoginTracker.objects.filter(
                    machine=machine,
                    browser_key=browser_key,
                    is_active=True
                ).first()
                
                if existing_tracker:
                    # Already logged in, just redirect
                    messages.info(request, f"Already logged into {machine.name}")
                else:
                    # Check if an inactive login exists
                    inactive_tracker = MachineLoginTracker.objects.filter(
                        machine=machine,
                        browser_key=browser_key,
                        is_active=False
                    ).first()
                    
                    if inactive_tracker:
                        # Reactivate it
                        inactive_tracker.is_active = True
                        inactive_tracker.save()
                        messages.success(request, f"Reactivated login for {machine.name}")
                    else:
                        # Create a new login
                        MachineLoginTracker.objects.create(
                            machine=machine,
                            browser_key=browser_key,
                            is_active=True
                        )
                        messages.success(request, f"Successfully logged into {machine.name}")
                
                # Store browser_key in session
                request.session['browser_key'] = browser_key
                request.session.save()
                
                return redirect('home')
            
            except Exception as e:
                # Handle any errors
                messages.error(request, f"Error logging into machine: {str(e)}")
                print(f"Machine login error: {str(e)}")
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MachineLoginForm()
    
    return render(request, 'core/machine_login.html', {'form': form})


def machine_logout(request):
    """Logs out from the current machine but keeps the browser key"""
    browser_key = request.session.get('browser_key')
    
    if browser_key:
        try:
            # Get all active machine logins for this browser
            active_logins = MachineLoginTracker.objects.filter(
                browser_key=browser_key,
                is_active=True
            )
            
            # Get the most recently accessed machine as the active one
            active_login = active_logins.order_by('-created_at').first()
            
            if active_login:
                machine_name = active_login.machine.name
                # Deactivate just this machine
                active_login.is_active = False
                active_login.save()
                messages.success(request, f"Successfully logged out from {machine_name}")
                
                # Check if there are other active machines
                remaining_active = MachineLoginTracker.objects.filter(
                    browser_key=browser_key,
                    is_active=True
                ).exists()
                
                if not remaining_active:
                    # If no active machines left, clear the browser key
                    request.session.pop('browser_key', None)
        except Exception as e:
            messages.error(request, f"Error logging out: {str(e)}")
            print(f"Machine logout error: {str(e)}")
    
    return redirect('home')


def debug_machine_login(request):
    """Debug view for machine login status"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
        
    browser_key = request.session.get('browser_key', 'No browser key in session')
    
    # Get all trackers for this browser key
    trackers = []
    if browser_key != 'No browser key in session':
        trackers = MachineLoginTracker.objects.filter(
            browser_key=browser_key
        ).select_related('machine').order_by('-created_at')
    
    # Get all active trackers across all browsers
    all_active_trackers = MachineLoginTracker.objects.filter(
        is_active=True
    ).select_related('machine').order_by('-created_at')
    
    context = {
        'browser_key': browser_key,
        'trackers': trackers,
        'all_active_trackers': all_active_trackers,
        'session_items': [(k, v) for k, v in request.session.items()]
    }
    
    return render(request, 'core/debug_machine_login.html', context)

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
    browser_key = request.session.get('browser_key')  # Get from session instead of GET parameter
    
    if not browser_key:
        return JsonResponse({
            'is_active': False,
            'machine_name': None,
            'error': 'No browser key in session'
        })
    
    active_machine_status = MachineLoginTracker.objects.filter(
        browser_key=browser_key,
        is_active=True
    ).select_related('machine').first()
    
    return JsonResponse({
        'is_active': bool(active_machine_status),
        'machine_name': active_machine_status.machine.name if active_machine_status else None,
        'browser_key': browser_key
    })

# Add to machineapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Machine
from django.contrib import messages

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def machine_checklist_config(request):
    """View for configuring which checklists to show for each machine"""
    machines = Machine.objects.all()
    
    if request.method == 'POST':
        # Process form submission
        for machine in machines:
            machine_id = str(machine.id)
            if machine_id in request.POST:
                # Update checklist settings for this machine
                machine.show_fixture_cleaning = 'show_fixture_cleaning_' + machine_id in request.POST
                machine.show_rejection_sheets = 'show_rejection_sheets_' + machine_id in request.POST
                machine.show_soldering_bit = 'show_soldering_bit_' + machine_id in request.POST
                machine.show_maintenance_checklist = 'show_maintenance_checklist_' + machine_id in request.POST
                machine.show_reading_list = 'show_reading_list_' + machine_id in request.POST
                machine.show_pchart = 'show_pchart_' + machine_id in request.POST
                machine.show_startup_checklist = 'show_startup_checklist_' + machine_id in request.POST
                machine.save()
        
        messages.success(request, "Machine checklist configuration updated successfully!")
        return redirect('machine_checklist_config')
    
    return render(request, 'machine_checklist_config.html', {'machines': machines})