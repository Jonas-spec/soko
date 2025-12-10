from django.urls import path, include

urlpatterns = [
    # ... other paths ...
    path('vendor/', include('vendor.urls')), # This connects the file above
    path('profile/', include(('users.urls', 'users'), namespace='users')),
]