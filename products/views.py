from django.shortcuts import render
from .models import Product

def product_list(request):
    # Filter for ACTIVE products. 
    # We generally show out-of-stock items (stock=0) but mark them as unavailable in the template,
    # OR you can filter them out here if you prefer: .filter(stock__gt=0)
    products = Product.objects.filter(status=Product.Status.ACTIVE)
    
    context = {
        'products': products,
    }
    return render(request, 'products/product_list.html', context)