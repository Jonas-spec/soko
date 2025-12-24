from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum, Count, F
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

# Local imports
from .models import Vendor
from orders.models import Order, OrderItem
from products.models import Product, Category
from .forms import VendorProfileForm, ProductForm

def vendor_required(view_func):
    """
    Decorator to ensure user is a vendor.
    Checks for both accounts.Vendor and vendor.models.Vendor.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'login_required': True,
                    'message': _('Please log in to access this page.')
                }, status=401)
            messages.warning(request, _('Please log in to access this page.'))
            return redirect('accounts:login')
        
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check for vendor profile (accounts.Vendor or vendor.models.Vendor)
        has_vendor = hasattr(request.user, 'vendor')
        has_vendor_profile = hasattr(request.user, 'vendor_profile')
        
        if not has_vendor and not has_vendor_profile:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'vendor_required': True,
                    'message': _('You need to register as a vendor to perform this action.')
                }, status=403)
            
            messages.warning(request, _('You need to register as a vendor to access this page.'))
            return redirect('vendor:become_vendor')
        
        # Check approval status - prefer accounts.Vendor if both exist
        vendor = None
        if has_vendor:
            vendor = request.user.vendor
        elif has_vendor_profile:
            vendor = request.user.vendor_profile
        
        if vendor and not vendor.is_approved:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'inactive_vendor': True,
                    'message': _('Your vendor account is currently inactive. Please contact support.')
                }, status=403)
            
            messages.warning(request, _('Your vendor account is currently inactive. Please contact support.'))
            return redirect('vendor:waiting_approval')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def become_vendor(request):
    """Allow a user to register as a vendor."""
    if hasattr(request.user, 'vendor_profile'):
        return redirect('vendor:dashboard')

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            messages.success(request, _('Vendor account created successfully!'))
            return redirect('vendor:dashboard')
    else:
        form = VendorProfileForm(initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    
    context = {'form': form}
    return render(request, 'vendor/become_vendor.html', context)

@login_required
@vendor_required
def dashboard(request):
    """Vendor dashboard view."""
    # Products use accounts.Vendor, so we need to get that
    from accounts.models import Vendor as AccountsVendor
    
    # Try to get vendor from accounts first (since products use accounts.Vendor)
    vendor = None
    if hasattr(request.user, 'vendor'):
        vendor = request.user.vendor
    elif hasattr(request.user, 'vendor_profile'):
        # If only vendor_profile exists, try to get or create accounts.Vendor
        vendor_profile = request.user.vendor_profile
        vendor, created = AccountsVendor.objects.get_or_create(
            user=request.user,
            defaults={
                'shop_name': vendor_profile.shop_name,
                'is_approved': vendor_profile.is_approved,
                'phone': vendor_profile.phone,
                'address': vendor_profile.address or '',
                'city': vendor_profile.city or '',
                'postal_code': vendor_profile.postal_code or '',
                'country': vendor_profile.country or '',
            }
        )
    else:
        messages.warning(request, _('User has no vendor profile.'))
        return redirect('vendor:become_vendor')
    
    # Get products using accounts.Vendor (which products reference)
    products = Product.objects.filter(vendor=vendor)
    total_products = products.count()
    out_of_stock = products.filter(stock=0).count()
    low_stock = products.filter(stock__gt=0, stock__lte=10).count()
    
    # Get orders - filter by products that belong to this vendor
    orders = Order.objects.filter(
        items__product__vendor=vendor
    ).distinct()
    total_orders = orders.count()
    
    STATUS_PENDING = getattr(Order.Status, 'PENDING', 'Pending')
    STATUS_COMPLETED = getattr(Order.Status, 'COMPLETED', getattr(Order.Status, 'DELIVERED', 'Delivered'))

    pending_orders = orders.filter(status=STATUS_PENDING).count()
    completed_orders = orders.filter(status=STATUS_COMPLETED).count()
    
    # Get recent orders
    recent_orders = orders.select_related(
        'customer'
    ).prefetch_related(
        'items', 'items__product'
    ).order_by('-created_at')[:5]
    
    # Get revenue
    total_revenue = orders.filter(
        status=STATUS_COMPLETED
    ).aggregate(
        total=Sum('total') 
    )['total'] or 0
    
    # Get monthly sales data
    today = timezone.now()
    monthly_sales = orders.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'total_revenue': total_revenue,
        'monthly_sales': monthly_sales,
        'vendor': vendor,
    }
    return render(request, 'vendor/dashboard.html', context)

@login_required
def add_category(request):
    """AJAX view to create a category on the fly."""
    if request.method == 'POST':
        name = request.POST.get('category_name')
        if name:
            if Category.objects.filter(name__iexact=name).exists():
                return JsonResponse({'success': False, 'error': 'Category already exists.'})
            
            category = Category.objects.create(
                name=name, 
                slug=slugify(name)
            )
            return JsonResponse({
                'success': True, 
                'id': category.id, 
                'name': category.name
            })
            
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@vendor_required
def order_list(request):
    """List all orders for the vendor."""
    # FIX: Use request.user.vendor_profile.id
    try:
        vendor_id = request.user.vendor_profile.id
    except AttributeError:
        return redirect('vendor:become_vendor')

    orders = Order.objects.filter(
        items__product__vendor__id=vendor_id
    ).select_related(
        'customer'
    ).prefetch_related(
        'items', 'items__product'
    ).distinct().order_by('-created_at')
    
    search_query = request.GET.get('q')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )
    
    status = request.GET.get('status')
    if status and status in dict(Order.Status.choices):
        orders = orders.filter(status=status)
    
    paginator = Paginator(orders, 25)
    page = request.GET.get('page')
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'status_choices': Order.Status.choices,
        'selected_status': status,
        'search_query': search_query or '',
    }
    return render(request, 'vendor/order_list.html', context)

@login_required
@vendor_required
def order_detail(request, order_id):
    """View order details."""
    try:
        vendor_id = request.user.vendor_profile.id
    except AttributeError:
        return redirect('vendor:become_vendor')

    order = get_object_or_404(
        Order.objects.select_related(
            'customer'
        ).prefetch_related(
            'items', 'items__product', 'activities'
        ),
        id=order_id,
        items__product__vendor__id=vendor_id
    )
    
    # FIX: Use ID filter here
    order_items = order.items.filter(product__vendor__id=vendor_id)
    
    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save(update_fields=['status', 'updated_at'])
            
            order.activities.create(
                user=request.user,
                status=new_status,
                note=request.POST.get('note', 'Status updated')
            )
            
            messages.success(request, _('Order status updated successfully.'))
            return redirect('vendor:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'order_items': order_items,
        'status_choices': Order.Status.choices,
    }
    return render(request, 'vendor/order_detail.html', context)

@login_required
@vendor_required
@require_http_methods(['POST'])
@csrf_exempt
def update_order_status(request, order_id):
    """Update order status via AJAX."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    try:
        vendor_id = request.user.vendor_profile.id
    except AttributeError:
        return JsonResponse({'success': False, 'error': 'Vendor profile not found'}, status=403)

    order = get_object_or_404(
        Order.objects.select_related('customer'),
        id=order_id,
        items__product__vendor__id=vendor_id
    )
    
    new_status = request.POST.get('status')
    if not new_status or new_status not in dict(Order.Status.choices):
        return JsonResponse(
            {'success': False, 'error': 'Invalid status'}, 
            status=400
        )
    
    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    
    order.activities.create(
        user=request.user,
        status=new_status,
        note=request.POST.get('note', 'Status updated via AJAX')
    )
    
    return JsonResponse({
        'success': True,
        'status': order.get_status_display(),
        'status_class': order.status.lower().replace(' ', '-'),
        'updated_at': order.updated_at.isoformat()
    })

class ProductListView(LoginRequiredMixin, ListView):
    """View for listing vendor's products."""
    model = Product
    template_name = 'vendor/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        # Products use accounts.Vendor, so get that
        from accounts.models import Vendor as AccountsVendor
        
        vendor = None
        if hasattr(self.request.user, 'vendor'):
            vendor = self.request.user.vendor
        elif hasattr(self.request.user, 'vendor_profile'):
            # Try to get or create accounts.Vendor
            vendor_profile = self.request.user.vendor_profile
            vendor, _ = AccountsVendor.objects.get_or_create(
                user=self.request.user,
                defaults={
                    'shop_name': vendor_profile.shop_name,
                    'is_approved': vendor_profile.is_approved,
                }
            )
        
        if not vendor:
            return Product.objects.none()
            
        queryset = Product.objects.filter(vendor=vendor)
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query) if hasattr(Product, 'sku') else Q()
            )
        
        status = self.request.GET.get('status')
        if status and hasattr(Product, 'status') and status in dict(Product.Status.choices):
            queryset = queryset.filter(status=status)
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'in_stock':
            queryset = queryset.filter(stock__gt=0)
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(stock=0)
        elif stock_status == 'low_stock':
            queryset = queryset.filter(stock__gt=0, stock__lte=10)
        
        return queryset.select_related('category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['status_choices'] = getattr(Product, 'Status', type('', (), {'choices': []})).choices if hasattr(Product, 'Status') else []
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['stock_status'] = self.request.GET.get('stock_status', '')
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'vendor/product_form.html'
    success_url = reverse_lazy('vendor:product_list')
    
    def form_valid(self, form):
        # 1. Create the object but do NOT save to DB yet
        product = form.save(commit=False)
        
        # 2. Manually assign the logged-in user's vendor profile
        if hasattr(self.request.user, 'vendor_profile'):
            product.vendor = self.request.user.vendor_profile
            
            # 3. Now save to the database
            product.save()
            
            messages.success(self.request, _('Product created successfully.'))
            return redirect(self.success_url)
        else:
            # Handle case where user isn't a vendor
            messages.error(self.request, _('You must have a vendor profile to add products.'))
            return redirect('vendor:become_vendor')
    
   # In accounts/views.py

# In vendor/views.py inside ProductCreateView

    def form_valid(self, form):
        # 1. Safety check
        if not hasattr(self.request.user, 'vendor_profile'):
            messages.error(self.request, _('No vendor profile found.'))
            return redirect('vendor:become_vendor')

        # 2. Get the product instance but don't save yet
        self.object = form.save(commit=False)
        
        # 3. FIX: Assign vendor_id directly instead of vendor object
        # This bypasses the "Must be Vendor instance" error
        self.object.vendor_id = self.request.user.vendor_profile.id
        
        # 4. Save to database
        self.object.save()
        
        messages.success(self.request, _('Product created successfully.'))
        return redirect(self.get_success_url())

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'vendor/product_form.html'
    success_url = reverse_lazy('vendor:product_list')
    
    def get_queryset(self):
        # FIX: Filter by ID
        if hasattr(self.request.user, 'vendor_profile'):
            return Product.objects.filter(vendor_id=self.request.user.vendor_profile.id)
        return Product.objects.none()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'vendor_profile'):
            kwargs['vendor'] = self.request.user.vendor_profile
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Product updated successfully.'))
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'vendor/product_confirm_delete.html'
    success_url = reverse_lazy('vendor:product_list')
    
    def get_queryset(self):
        # FIX: Filter by ID
        if hasattr(self.request.user, 'vendor_profile'):
            return Product.objects.filter(vendor_id=self.request.user.vendor_profile.id)
        return Product.objects.none()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Product has been deleted.'))
        return super().delete(request, *args, **kwargs)

@login_required
@vendor_required
def vendor_profile(request):
    try:
        vendor = request.user.vendor_profile
    except ObjectDoesNotExist:
        messages.warning(request, _('User has no vendor profile.'))
        return redirect('vendor:become_vendor')
    
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email', '')
            
            new_password = form.cleaned_data.get('new_password1')
            if new_password:
                user.set_password(new_password)
            
            user.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('vendor:profile')
    else:
        form = VendorProfileForm(instance=vendor, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    
    context = {'form': form, 'vendor': vendor}
    return render(request, 'vendor/profile.html', context)

@login_required
@vendor_required
def analytics(request):
    """Vendor analytics dashboard."""
    try:
        vendor = request.user.vendor_profile
    except ObjectDoesNotExist:
        return redirect('vendor:become_vendor')

    STATUS_COMPLETED = getattr(Order.Status, 'COMPLETED', getattr(Order.Status, 'DELIVERED', 'Delivered'))

    # Date ranges
    today = timezone.now().date()
    last_week = today - timezone.timedelta(days=7)
    last_month = today - timezone.timedelta(days=30)
    
    # Sales data
    # FIX: Use ID filter
    orders = Order.objects.filter(
        items__product__vendor__id=vendor.id,
        status=STATUS_COMPLETED
    ).distinct()
    
    total_sales = orders.aggregate(total=Sum('total'))['total'] or 0
    weekly_sales = orders.filter(
        created_at__date__gte=last_week
    ).aggregate(total=Sum('total'))['total'] or 0
    monthly_sales = orders.filter(
        created_at__date__gte=last_month
    ).aggregate(total=Sum('total'))['total'] or 0
    
    order_count = orders.count()
    weekly_orders = orders.filter(created_at__date__gte=last_week).count()
    monthly_orders = orders.filter(created_at__date__gte=last_month).count()
    
    top_products = Product.objects.filter(
        order_items__order__in=orders
    ).annotate(
        total_sold=Sum('order_items__quantity'),
        revenue=Sum('order_items__price')
    ).order_by('-total_sold')[:5]
    
    sales_by_day = orders.filter(
        created_at__date__gte=last_month
    ).values('created_at__date').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('created_at__date')
    
    context = {
        'vendor': vendor,
        'total_sales': total_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'order_count': order_count,
        'weekly_orders': weekly_orders,
        'monthly_orders': monthly_orders,
        'top_products': top_products,
        'sales_by_day': sales_by_day,
    }
    return render(request, 'vendor/analytics.html', context)

@login_required
@vendor_required
def settings(request):
    """Vendor settings view."""
    try:
        vendor = request.user.vendor_profile
    except ObjectDoesNotExist:
        return redirect('vendor:become_vendor')

    if request.method == 'POST':
        if 'notifications' in request.POST:
            vendor.email_notifications = 'email_notifications' in request.POST
            vendor.sms_notifications = 'sms_notifications' in request.POST
            vendor.save()
            messages.success(request, _('Notification preferences updated.'))
            return redirect('vendor:settings')
        elif 'store_settings' in request.POST:
            vendor.store_name = request.POST.get('store_name', '')
            vendor.store_description = request.POST.get('store_description', '')
            vendor.store_phone = request.POST.get('store_phone', '')
            vendor.store_email = request.POST.get('store_email', '')
            vendor.save()
            messages.success(request, _('Store settings updated.'))
            return redirect('vendor:settings')
    
    context = {'vendor': vendor}
    return render(request, 'vendor/settings.html', context)

@login_required
def waiting_approval(request):
    """
    Page shown to vendors who have registered but are not yet approved.
    """
    # Check for vendor_profile first (vendor app model)
    if hasattr(request.user, 'vendor_profile'):
        if request.user.vendor_profile.is_approved:
            messages.info(request, 'Your vendor account is already approved.')
            return redirect('vendor:dashboard')
        vendor = request.user.vendor_profile
    # Check for vendor (accounts app model)
    elif hasattr(request.user, 'vendor'):
        if request.user.vendor.is_approved:
            messages.info(request, 'Your vendor account is already approved.')
            return redirect('vendor:dashboard')
        vendor = request.user.vendor
    else:
        messages.error(request, 'You need to register as a vendor first.')
        return redirect('vendor:become_vendor')
        
    context = {
        'vendor': vendor
    }
    return render(request, 'vendor/waiting_approval.html', context)
    # In vendor/views.py
@login_required
def vendor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'login_required': True,
                    'message': _('Please log in to access this page.')
                }, status=401)
            messages.warning(request, _('Please log in to access this page.'))
            return redirect('accounts:login')
        
        # Allow staff to bypass vendor checks
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check if vendor profile exists
        if not hasattr(request.user, 'vendor'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'vendor_required': True,
                    'message': _('You need to register as a vendor to perform this action.')
                }, status=403)
            messages.warning(request, _('You need to register as a vendor to access this page.'))
            return redirect('vendor:become_vendor')
        
        # Check approval status
        if not request.user.vendor.is_approved:
            if request.path == reverse('vendor:waiting_approval'):
                return view_func(request, *args, **kwargs)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'inactive_vendor': True,
                    'message': _('Your vendor account is pending approval.')
                }, status=403)
            
            messages.warning(request, _('Your vendor account is pending approval.'))
            return redirect('vendor:waiting_approval')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view