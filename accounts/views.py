from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse  # Added reverse to imports
from .models import User
from .forms import UserRegisterForm, UserChangeForm  # Added UserChangeForm import

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

class CustomLoginView(LoginView):
    def get_success_url(self):
        try:
            if hasattr(self.request.user, 'is_vendor') and self.request.user.is_vendor:
                # Try to resolve the vendor dashboard URL
                return reverse('vendor:dashboard')
        except:
            # Fall back to home if vendor namespace doesn't exist
            pass
        return reverse('home')