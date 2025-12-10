from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CustomerProfileForm
from .models import Customer

# Import your forms
from .forms import UserRegistrationForm, UserChangeForm, VendorProfileForm, CustomerProfileForm

# Import your models
from .models import Vendor, Customer

class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')
    authentication_form = AuthenticationForm  # Explicitly set the form class

    def form_invalid(self, form):
        """Handle invalid form submission."""
        response = super().form_invalid(form)
        # Clear any existing messages to prevent duplicates
        storage = messages.get_messages(self.request)
        storage.used = True
        return response


def logout_view(request):
    """
    Allow logout via GET or POST and redirect home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        
        # Check if user is active
        if not user.is_active:
            messages.error(self.request, 'Your account is inactive. Please contact support.')
            return self.form_invalid(form)
            
        # Check if vendor is approved
        if hasattr(user, 'vendor') and not user.vendor.is_approved:
            login(self.request, user)
            messages.warning(self.request, 'Your vendor account is pending approval.')
            return redirect('vendor:waiting_approval')
            
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            return reverse('admin:index')
            
        if hasattr(user, 'vendor'):
            if user.vendor.is_approved:
                return reverse('vendor:dashboard')
            return reverse('vendor:waiting_approval')
            
        # Default redirect for customers and other users
        return reverse('home')
        
class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        user.email = form.cleaned_data.get('email')
        user.save()

        user_type = form.cleaned_data.get('user_type')
        if user_type == 'customer':
            Customer.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )
        elif user_type == 'vendor':
            # Use cleaned data validated in the form to avoid integrity errors
            Vendor.objects.create(
                user=user,
                shop_name=form.cleaned_data['shop_name'],
                description=form.cleaned_data.get('description', ''),
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
                city=form.cleaned_data.get('city', ''),
                postal_code=form.cleaned_data.get('postal_code', ''),
                country=form.cleaned_data.get('country', ''),
                is_approved=False  # New vendors need admin approval
            )
        
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

@login_required
def profile(request):
    """
    Allows users to edit their basic profile information.
    Handles both User and profile model updates.
    """
    user = request.user
    profile = None
    
    # Determine the profile type
    if hasattr(user, 'vendor'):
        profile = user.vendor
        profile_form_class = VendorProfileForm
    elif hasattr(user, 'customer'):
        profile = user.customer
        profile_form_class = CustomerProfileForm
    else:
        # If no profile exists, redirect to registration
        messages.warning(request, 'Please complete your profile setup.')
        return redirect('accounts:register_additional')

    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=user)
        profile_form = profile_form_class(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserChangeForm(instance=user)
        profile_form = profile_form_class(instance=profile)
    
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'is_vendor': hasattr(user, 'vendor'),
        'is_customer': hasattr(user, 'customer')
    })

@login_required
def profile_complete(request):
    """
    Check if the user has completed their profile.
    If not, redirect to the appropriate profile completion page.
    """
    user = request.user
    
    if hasattr(user, 'customer') or hasattr(user, 'vendor'):
        return redirect('home')
        
    # If user has no profile, determine which one to create
    if 'user_type' in request.session:
        if request.session['user_type'] == 'vendor':
            return redirect('vendor:become_vendor')
        return redirect('accounts:complete_customer_profile')
    
    return redirect('accounts:register_additional')

@login_required
def home(request):
    # If user is not authenticated, redirect to login
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('accounts:login') + '?next=' + request.path)
        
    # If user is authenticated but has no profile, redirect to profile completion
    if not hasattr(request.user, 'vendor') and not hasattr(request.user, 'customer'):
        from django.shortcuts import redirect
        return redirect('accounts:complete_profile')
        
    return render(request, 'home.html')

def complete_profile(request):
    """
    View for users to complete their profile after registration.
    This will determine if they need to complete vendor or customer profile.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
        
    # If user already has a profile, redirect to home
    if hasattr(request.user, 'vendor') or hasattr(request.user, 'customer'):
        return redirect('home')
        
    # Check user_type from session
    user_type = request.session.get('user_type')
    
    if user_type == 'vendor':
        return redirect('vendor:become_vendor')
    elif user_type == 'customer':
        return redirect('accounts:complete_customer_profile')
    else:
        # If no user_type in session, redirect to registration
        return redirect('accounts:register')

def complete_customer_profile(request):
    """
    View for customers to complete their profile after registration.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
        
    # If user already has a customer profile, redirect to home
    if hasattr(request.user, 'customer'):
        return redirect('home')
        
    # If user is a vendor, redirect to vendor dashboard
    if hasattr(request.user, 'vendor'):
        return redirect('vendor:dashboard')
    
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            # Create customer profile
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home')
    else:
        form = CustomerProfileForm(initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    
    return render(request, 'accounts/complete_customer_profile.html', {
        'form': form
    })