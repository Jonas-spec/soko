from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
import stripe
import json

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

@login_required
def cart(request):
    """Display shopping cart."""
    # Get or create cart order for user
    order, created = Order.objects.get_or_create(
        customer=request.user,
        status=Order.Status.PENDING,
        defaults={
            'total': 0,
            'delivery_address': '',
            'phone': ''
        }
    )
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if not product.is_available:
        messages.error(request, 'Product is not available.')
        return JsonResponse({'success': False, 'message': 'Product not available'})
    
    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock.')
        return JsonResponse({'success': False, 'message': 'Insufficient stock'})
    
    # Get or create pending order
    order, created = Order.objects.get_or_create(
        customer=request.user,
        status=Order.Status.PENDING,
        defaults={'total': 0, 'delivery_address': '', 'phone': ''}
    )
    
    # Add or update order item
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'quantity': quantity, 'price': product.price}
    )
    
    if not created:
        order_item.quantity += quantity
        if order_item.quantity > product.stock:
            order_item.quantity = product.stock
        order_item.save()
    
    order.update_total()
    messages.success(request, f'{product.name} added to cart!')
    
    return JsonResponse({
        'success': True,
        'message': 'Product added to cart',
        'cart_count': order.items.count()
    })

@login_required
@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        item.delete()
        messages.success(request, 'Item removed from cart.')
    elif quantity > item.product.stock:
        messages.error(request, f'Only {item.product.stock} items available.')
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cart updated.')
    
    return redirect('orders:cart')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('orders:cart')

@login_required
def checkout(request):
    """Checkout page with Stripe payment."""
    order = get_object_or_404(
        Order,
        customer=request.user,
        status=Order.Status.PENDING
    )
    
    if order.items.count() == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')
    
    # Check stock availability
    for item in order.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} is out of stock.')
            return redirect('orders:cart')
    
    # Get Stripe publishable key
    stripe_publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
    
    context = {
        'order': order,
        'stripe_publishable_key': stripe_publishable_key,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
@require_POST
@transaction.atomic
def process_payment(request):
    """Process Stripe payment."""
    order = get_object_or_404(
        Order,
        customer=request.user,
        status=Order.Status.PENDING
    )
    
    if order.items.count() == 0:
        return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
    try:
        # Get payment details from request
        token = request.POST.get('stripeToken')
        delivery_address = request.POST.get('delivery_address', '')
        phone = request.POST.get('phone', '')
        
        if not delivery_address or not phone:
            return JsonResponse({
                'success': False,
                'message': 'Please provide delivery address and phone number'
            })
        
        # Update order with delivery info
        order.delivery_address = delivery_address
        order.phone = phone
        
        # Create Stripe charge
        charge = stripe.Charge.create(
            amount=int(order.total * 100),  # Convert to cents
            currency='usd',
            description=f'Order #{order.id}',
            source=token,
        )
        
        # Update order status and reduce stock
        order.status = Order.Status.PROCESSING
        order.save()
        
        # Reduce product stock
        for item in order.items.all():
            item.product.reduce_stock(item.quantity)
        
        messages.success(request, f'Payment successful! Order #{order.id} has been placed.')
        return JsonResponse({
            'success': True,
            'message': 'Payment processed successfully',
            'order_id': order.id
        })
        
    except stripe.error.CardError as e:
        messages.error(request, f'Card error: {e.user_message}')
        return JsonResponse({'success': False, 'message': str(e)})
    except stripe.error.StripeError as e:
        messages.error(request, 'Payment processing error. Please try again.')
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again.')
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def order_history(request):
    """Display user's order history."""
    orders = Order.objects.filter(
        customer=request.user
    ).exclude(status=Order.Status.PENDING).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Display order details."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order_detail.html', context)
