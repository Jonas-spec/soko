from django.contrib import admin
from .models import Vendor, Customer

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'is_approved', 'phone', 'city', 'created_at']
    list_filter = ['is_approved', 'country', 'created_at']
    search_fields = ['shop_name', 'user__username', 'user__email', 'phone', 'city']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'shop_name', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'postal_code', 'country')
        }),
        ('Status', {
            'fields': ('is_approved', 'created_at')
        }),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address']
    search_fields = ['user__username', 'user__email', 'phone', 'address']
