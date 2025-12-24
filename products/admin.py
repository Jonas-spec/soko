from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # REMOVED prepopulated_fields because Product has no slug
    list_display = ['name', 'vendor', 'category', 'price', 'stock', 'status', 'is_available_display']
    list_filter = ['status', 'category', 'vendor']
    search_fields = ['name', 'description', 'vendor__shop_name']
    
    # Enable autocomplete for vendor and category - this adds the "+" button to add new ones
    autocomplete_fields = ['vendor', 'category']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'vendor')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'status')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )
    
    def is_available_display(self, obj):
        return obj.is_available
    is_available_display.boolean = True
    is_available_display.short_description = 'Available'
