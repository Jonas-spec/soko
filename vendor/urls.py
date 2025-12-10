from django.urls import path
from django.views.generic import RedirectView  # <--- This import fixes your error
from . import views

app_name = 'vendor'

urlpatterns = [
    # --- Dashboard & Core ---
    # This redirects http://127.0.0.1:8000/vendor/ directly to /vendor/dashboard/
    path('', RedirectView.as_view(pattern_name='vendor:dashboard'), name='vendor_home'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('profile/', views.vendor_profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('analytics/', views.analytics, name='analytics'),
    path('waiting-approval/', views.waiting_approval, name='waiting_approval'),

    # --- Product Management ---
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # --- Order Management ---
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),

    # --- Category AJAX ---
    path('category/add-ajax/', views.add_category, name='add_category_ajax'),
]