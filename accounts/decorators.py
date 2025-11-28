# accounts/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from functools import wraps

def vendor_required(view_func):
    """
    Decorator for views that checks that the user is a vendor, redirecting
    to the login page if necessary.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('login')
        if not hasattr(request.user, 'is_vendor') or not request.user.is_vendor:
            messages.warning(request, 'You do not have permission to access this page.')
            return redirect('products:list')  # Or any other appropriate page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def customer_required(view_func):
    """
    Decorator for views that checks that the user is a customer, redirecting
    to the login page if necessary.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('login')
        if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
            messages.warning(request, 'You do not have permission to access this page.')
            return redirect('vendor:dashboard' if hasattr(request.user, 'is_vendor') and request.user.is_vendor else 'products:list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view