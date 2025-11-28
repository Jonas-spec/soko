# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleBasedAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        if not hasattr(view_func, 'view_class'):
            return None

        view_class = view_func.view_class
        if hasattr(view_class, 'vendor_required') and view_class.vendor_required:
            if not request.user.is_authenticated or not hasattr(request.user, 'is_vendor') or not request.user.is_vendor:
                messages.error(request, "Vendor access required.")
                return redirect(reverse('login'))

        if hasattr(view_class, 'customer_required') and view_class.customer_required:
            if not request.user.is_authenticated or not hasattr(request.user, 'is_customer') or not request.user.is_customer:
                messages.error(request, "Customer access required.")
                return redirect(reverse('login'))

        return None