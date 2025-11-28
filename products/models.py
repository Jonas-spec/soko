from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class Product(models.Model):
    """
    Product model representing items for sale in the marketplace.
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        DRAFT = 'draft', _('Draft')

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('vendor')
    )
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
            models.Index(fields=['name'], name='name_idx'),
            models.Index(fields=['price'], name='price_idx'),
            models.Index(fields=['status'], name='status_idx'),
        ]

    def __str__(self):
        return f"{self.name} - ${self.price}"

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
