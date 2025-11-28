from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Vendor(models.Model):
    """
    Vendor model representing a seller in the marketplace.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('user')
    )
    shop_name = models.CharField(
        _('shop name'),
        max_length=100
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        null=True
    )
    address = models.TextField(
        _('address'),
        blank=True,
        null=True
    )
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20,
        blank=True,
        null=True
    )
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        null=True
    )
    is_approved = models.BooleanField(
        _('is approved'),
        default=False,
        help_text=_('Designates whether this vendor is approved to sell on the platform.')
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
        verbose_name = _('vendor')
        verbose_name_plural = _('vendors')
        ordering = ['-created_at']

    def __str__(self):
        return self.shop_name
        
    @property
    def total_products(self):
        """Return the total number of products for this vendor."""
        from products.models import Product
        return Product.objects.filter(vendor=self.user).count()
        
    @property
    def total_orders(self):
        """Return the total number of orders for this vendor."""
        from orders.models import Order
        return Order.objects.filter(vendor=self.user).count()
