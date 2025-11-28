from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Vendor

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['shop_name', 'phone', 'address', 'city', 'postal_code', 'country', 'logo']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
