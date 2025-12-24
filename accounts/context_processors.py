# accounts/context_processors.py
def user_context(request):
    """
    Add user-related context variables to all templates.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Check if user has vendor profile (accounts.Vendor)
        has_vendor = False
        has_vendor_profile = False
        
        try:
            has_vendor = hasattr(request.user, 'vendor') and request.user.vendor is not None
        except:
            pass
        
        try:
            has_vendor_profile = hasattr(request.user, 'vendor_profile') and request.user.vendor_profile is not None
        except:
            pass
        
        context['is_vendor'] = has_vendor or has_vendor_profile
        context['is_customer'] = hasattr(request.user, 'customer') and request.user.customer is not None
    else:
        context['is_vendor'] = False
        context['is_customer'] = False
    
    return context
