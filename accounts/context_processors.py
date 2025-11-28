# accounts/context_processors.py
def user_type(request):
    return {
        'is_vendor': hasattr(request.user, 'is_vendor') and request.user.is_vendor,
        'is_customer': hasattr(request.user, 'is_customer') and request.user.is_customer,
    }