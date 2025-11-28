# sokohub/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView


def test_view(request):
    return HttpResponse("Test page")
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('test/', test_view, name='test'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls', namespace='products')),
    path('vendor/', include('vendor.urls', namespace='vendor')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)