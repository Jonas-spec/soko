from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category

def product_list(request):
    """
    Display all active products for browsing.
    Users don't need to be logged in to browse products.
    """
    # Filter for ACTIVE products
    products = Product.objects.filter(status=Product.Status.ACTIVE).select_related('vendor', 'category').order_by('-created_at')
    
    # Get categories for filtering (optional)
    categories = Category.objects.filter(is_active=True)
    
    # Get search query if provided
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get category filter if provided
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    }
    return render(request, 'products/product_list.html', context)