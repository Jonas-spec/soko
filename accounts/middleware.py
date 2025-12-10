# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

# accounts/middleware.py
class RoleBasedAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for login and other auth views
        if request.path.startswith('/accounts/'):
            return None

        if not hasattr(view_func, 'view_class'):
            return None

        view_class = view_func.view_class
        
        # Check for vendor_required
        if hasattr(view_class, 'vendor_required') and view_class.vendor_required:
            if not request.user.is_authenticated or not hasattr(request.user, 'vendor'):
                messages.error(request, "Vendor access required.")
                return redirect(reverse('accounts:login'))

        # Check for customer_required
        if hasattr(view_class, 'customer_required') and view_class.customer_required:
            if not request.user.is_authenticated or not hasattr(request.user, 'customer'):
                messages.error(request, "Customer access required.")
                return redirect(reverse('accounts:login'))

        return None