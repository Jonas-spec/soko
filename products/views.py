# products/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import customer_required

@login_required
@customer_required
def product_list(request):
    # Your view logic here
    return render(request, 'products/product_list.html')