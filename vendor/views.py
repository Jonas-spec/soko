# vendor/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Local imports
from .models import Vendor
from orders.models import Order, OrderItem
from products.models import Product

def vendor_required(view_func):
    """
    Decorator to ensure user is a vendor.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'vendor_profile'):
            messages.warning(request, _('You are not registered as a vendor.'))
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@vendor_required
def dashboard(request):
    """Vendor dashboard view."""
    vendor = request.user.vendor_profile
    
    # Get recent orders
    recent_orders = Order.objects.filter(
        items__product__vendor=request.user
    ).distinct().order_by('-created_at')[:5]
    
    # Get order statistics
    total_orders = Order.objects.filter(
        items__product__vendor=request.user
    ).distinct().count()
    
    # Get product statistics
    total_products = Product.objects.filter(vendor=request.user).count()
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_products': total_products,
        'vendor': vendor,
    }
    return render(request, 'vendor/dashboard.html', context)

@login_required
@vendor_required
def order_list(request):
    """List all orders for the vendor."""
    # Get orders that have at least one product from this vendor
    orders_list = Order.objects.filter(
        items__product__vendor=request.user
    ).distinct().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        orders_list = orders_list.filter(
            Q(id__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    return render(request, 'vendor/order_list.html', {
        'orders': orders,
        'status_choices': Order.Status.choices,
        'status_filter': status_filter,
        'search_query': search_query or ''
    })

@login_required
@vendor_required
def order_detail(request, order_id):
    """View order details."""
    # Get the order and filter by items that belong to this vendor
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.filter(product__vendor=request.user).select_related('product')
    
    if not order_items.exists():
        messages.warning(request, _('Order not found or you do not have permission to view it.'))
        return redirect('vendor:order_list')
    
    # Update order status if POST request
    if request.method == 'POST' and 'status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save(update_fields=['status'])
            
            # Add activity log entry
            order.activities.create(
                user=request.user,
                status=new_status,
                note=_('Status updated by vendor')
            )
            
            messages.success(request, _('Order status updated to %(status)s') % {
                'status': order.get_status_display()
            })
            return redirect('vendor:order_detail', order_id=order.id)
    
    # Get order activities
    activities = order.activities.select_related('user').order_by('-created_at')
    
    return render(request, 'vendor/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'status_choices': Order.Status.choices,
        'activities': activities
    })

@login_required
@vendor_required
def update_order_status(request, order_id):
    """Update order status via AJAX."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Verify the order has items from this vendor
        if not order.items.filter(product__vendor=request.user).exists():
            return JsonResponse({
                'success': False,
                'error': _('Order not found or access denied')
            }, status=404)
        
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save(update_fields=['status'])
            
            # Add activity log entry
            order.activities.create(
                user=request.user,
                status=new_status,
                note=_('Status updated by vendor via AJAX')
            )
            
            return JsonResponse({
                'success': True,
                'status': order.get_status_display(),
                'status_class': order.status,
                'updated': order.updated_at.isoformat()
            })
    
    return JsonResponse({
        'success': False,
        'error': _('Invalid request')
    }, status=400)

class ProductListView(LoginRequiredMixin, ListView):
    """View for listing vendor's products."""
    model = Product
    template_name = 'vendor/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.filter(vendor=self.request.user)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query) if hasattr(Product, 'sku') else Q()
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and hasattr(Product, 'status') and status in dict(Product.Status.choices):
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = getattr(Product, 'Status', type('', (), {'choices': []}))
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new product."""
    model = Product
    template_name = 'vendor/product_form.html'
    fields = [
        'name', 'description', 'price', 'stock', 'image', 
        'category', 'is_available'
    ]
    success_url = reverse_lazy('vendor:product_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Customize form fields if needed
        form.fields['description'].widget.attrs['rows'] = 3
        return form

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        messages.success(self.request, _('Product created successfully.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        if 'save_and_add_another' in self.request.POST:
            return reverse_lazy('vendor:add_product')
        return super().get_success_url()

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing product."""
    model = Product
    template_name = 'vendor/product_form.html'
    fields = [
        'name', 'description', 'price', 'stock', 'image', 
        'category', 'is_available'
    ]
    success_url = reverse_lazy('vendor:product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Customize form fields if needed
        form.fields['description'].widget.attrs['rows'] = 3
        return form
    
    def form_valid(self, form):
        messages.success(self.request, _('Product updated successfully.'))
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a product."""
    model = Product
    template_name = 'vendor/product_confirm_delete.html'
    success_url = reverse_lazy('vendor:product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Product has been deleted.'))
        return super().delete(request, *args, **kwargs)

@login_required
@vendor_required
def vendor_profile(request):
    """View for vendor profile management."""
    vendor = request.user.vendor_profile
    
    if request.method == 'POST':
        # Handle profile update
        vendor_form = VendorProfileForm(
            request.POST, 
            request.FILES, 
            instance=vendor
        )
        
        if vendor_form.is_valid():
            vendor = vendor_form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            
            # Update user details if needed
            user = request.user
            if 'first_name' in request.POST:
                user.first_name = request.POST.get('first_name', '')
            if 'last_name' in request.POST:
                user.last_name = request.POST.get('last_name', '')
            if 'email' in request.POST:
                user.email = request.POST.get('email', '')
            
            # Handle password change if provided
            new_password = request.POST.get('new_password1')
            if new_password and new_password == request.POST.get('new_password2'):
                user.set_password(new_password)
            
            user.save()
            
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('vendor:profile')
    else:
        vendor_form = VendorProfileForm(instance=vendor)
    
    return render(request, 'vendor/profile.html', {
        'vendor': vendor,
        'form': vendor_form,
    })