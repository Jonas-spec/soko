# vendor/urls.py
from django.urls import path
from django.views.decorators.http import require_http_methods
from . import views

app_name = 'vendor'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', 
         require_http_methods(['POST'])(views.update_order_status), 
         name='update_order_status'),
    
    # Products - Updated to use class-based views
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='add_product'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),
    
    # Profile
    path('profile/', views.vendor_profile, name='vendor_profile'),
]