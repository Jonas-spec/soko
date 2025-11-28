from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product

class Order(models.Model):
    """
    Order model representing a customer's order.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('customer')
    )
    total = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    delivery_address = models.TextField(
        _('delivery address'),
        help_text=_('Full delivery address including city and postal code')
    )
    phone = models.CharField(
        _('contact phone'),
        max_length=20,
        help_text=_('Contact phone number for delivery updates')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='order_status_idx'),
            models.Index(fields=['created_at'], name='order_created_at_idx'),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()} (${self.total})"

    @property
    def item_count(self):
        """Return total number of items in the order."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def update_total(self):
        """Update the order total based on order items."""
        self.total = sum(
            item.price * item.quantity
            for item in self.items.all()
        )
        self.save(update_fields=['total', 'updated_at'])


class OrderItem(models.Model):
    """
    OrderItem model representing a single item within an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('product')
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        _('price at time of purchase'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_product'
            )
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (${self.price} each)"

    @property
    def total_price(self):
        """Calculate total price for this order item."""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Override save to update order total when item is saved."""
        super().save(*args, **kwargs)
        self.order.update_total()

    def delete(self, *args, **kwargs):
        """Override delete to update order total when item is deleted."""
        order = self.order
        super().delete(*args, **kwargs)
        order.update_total()