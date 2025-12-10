from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class Category(models.Model):
    """
    Category model for grouping products.
    """
    name = models.CharField(
        _('name'),
        max_length=100
    )
    slug = models.SlugField(
        _('slug'),
        unique=True,
        help_text=_('Unique identifier for URL.')
    )
    description = models.TextField(
        _('description'),
        blank=True
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True
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
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active'], name='cat_active_idx'),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model representing items for sale in the Soko Hub marketplace.
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        DRAFT = 'draft', _('Draft')

    # Relationships
    vendor = models.ForeignKey(
        'accounts.Vendor',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('vendor')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # Prevents deleting a category if it has products
        related_name='products',
        verbose_name=_('category')
    )

    # Basic Info
    name = models.CharField(
        _('product name'),
        max_length=200
    )
    description = models.TextField(
        _('description'),
        blank=True
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(
        _('stock quantity'),
        default=0
    )
    image = models.ImageField(
        _('product image'),
        upload_to='products/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    # State
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
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
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name'], name='prod_name_idx'),
            models.Index(fields=['price'], name='prod_price_idx'),
            models.Index(fields=['status'], name='prod_status_idx'),
        ]

    def __str__(self):
        return f"{self.name} - {self.price}"

    @property
    def is_available(self):
        """Check if product is available for purchase."""
        return self.status == self.Status.ACTIVE and self.stock > 0

    def reduce_stock(self, quantity):
        """
        Reduce the product stock by the given quantity.
        Returns True if successful, False otherwise.
        """
        if quantity <= 0:
            return False
        if self.stock >= quantity:
            self.stock -= quantity
            self.save(update_fields=['stock', 'updated_at'])
            return True
        return False