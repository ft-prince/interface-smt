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



# ----------------------------------------------------------------
# crud methods
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

@login_required
def profile_list(request):
    profiles = Profile.objects.all()
    return render(request, 'user_app/profile_list.html', {'profiles': profiles})

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'user_app/profile_detail.html', {'profile': profile})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile
from django.contrib import messages

@login_required
def profile_create(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']  # Get the selected user
            if Profile.objects.filter(user=user).exists():
                messages.error(request, f"A profile already exists for {user.username}.")
            else:
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, f"Profile created for {user.username}.")
                return redirect('profile_detail', pk=profile.pk)
    else:
        form = ProfileForm()
    
    return render(request, 'user_app/profile_form.html', {'form': form})

@login_required
def profile_update(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', pk=profile.pk)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'user_app/profile_form.html', {'form': form})

@login_required
def profile_delete(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == 'POST':
        profile.delete()
        return redirect('profile_list')
    return render(request, 'user_app/profile_confirm_delete.html', {'profile': profile})
