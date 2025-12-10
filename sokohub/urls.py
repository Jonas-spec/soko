from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from accounts import views as account_views

# Import the debug_templates view
from sokohub.views import debug_templates

def test_view(request):
    return HttpResponse("Test page")


urlpatterns = [
   # --- Admin & Core ---
    path('admin/', admin.site.urls),
    path('', account_views.home, name='home'), # This will use the home view from accounts/urls.py

    # --- Authentication (The Fixed Section) ---
    # We use 'accounts/' ONLY for your main accounts app.
    # The 'namespace' ensures you can use tags like {% url 'accounts:login' %}
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

    # We moved 'users' to 'profile/' to avoid the "Namespace isn't unique" error.
    path('profile/', include(('users.urls', 'users'), namespace='users')),
    # NOTE: If you decide to use django-allauth later, enable this line 
    # but keep it at a different URL (like 'auth/') to avoid conflicts.
    # path('auth/', include('allauth.urls')),

    # --- Main Features ---
    path('vendor/', include(('vendor.urls', 'vendor'), namespace='vendor')),
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # --- Debugging & Test Views ---
    path('test/', test_view, name='test'),
    path('debug-templates/', debug_templates, name='debug_templates'),
]

# Serving static + media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
