from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse

# Import the debug_templates view
from sokohub.views import debug_templates

def test_view(request):
    return HttpResponse("Test page")


urlpatterns = [
    path('test/', test_view, name='test'),
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Debug template paths page
    path('debug-templates/', debug_templates, name='debug_templates'),

    # App URLs
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('vendor/', include(('vendor.urls', 'vendor'), namespace='vendor')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
]

# Serving static + media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
