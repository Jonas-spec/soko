from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Vendor, Customer
# If Product is in a different app (e.g., 'products'), keep this import. 
# If it's in the same app, use .models import Product
from products.models import Product 

# --- 1. REGISTRATION FORM ---
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Confirm Password'
    }))
    # Vendor-specific fields (optional unless user_type is vendor)
    shop_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Shop name (vendors only)'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Short description',
            'rows': 3,
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +1234567890'
        })
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal code'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    USER_TYPES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPES, 
        widget=forms.RadioSelect,
        label="I want to sign up as:"
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            # non-model fields must be listed so they render/validate
            'confirm_password',
            'user_type',
            'shop_name',
            'description',
            'phone',
            'address',
            'city',
            'postal_code',
            'country',
        ]
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        user_type = cleaned_data.get("user_type")
        shop_name = (cleaned_data.get("shop_name") or "").strip()

        if password != confirm_password:
            raise ValidationError("Password and Confirm Password does not match")

        if user_type == "vendor":
            if not shop_name:
                raise ValidationError("Shop name is required for vendors.")
            # Enforce uniqueness at the form level to avoid DB integrity errors
            if Vendor.objects.filter(shop_name__iexact=shop_name).exists():
                raise ValidationError("A vendor with this shop name already exists.")

        cleaned_data["shop_name"] = shop_name  # persist stripped value
        return cleaned_data

    def save(self, commit=True):
        """
        Ensure the password is hashed when creating the User instance.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# --- 2. USER CHANGE FORM (For Profile Updates) ---
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

# --- 3. CUSTOMER PROFILE FORM ---
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address']
    
    def __init__(self, *args, **kwargs):
        super(CustomerProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field == 'phone':
                self.fields[field].widget.attrs['placeholder'] = 'e.g. +1234567890'

# --- 4. VENDOR PROFILE FORM ---
class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'shop_name', 
            'logo', 
            'phone', 
            'address', 
            'city', 
            'postal_code', 
            'country'
        ]

    def __init__(self, *args, **kwargs):
        super(VendorProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        if 'logo' in self.fields:
            self.fields['logo'].widget.attrs['class'] = 'form-control-file'

# --- 4. PRODUCT FORM ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name', 
            'description', 
            'price', 
            'stock', 
            'image', 
            'status'
        ]
        
    def __init__(self, *args, **kwargs):
        # Remove 'vendor' from kwargs if it exists to prevent errors
        if 'vendor' in kwargs:
            kwargs.pop('vendor')
            
        super(ProductForm, self).__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['description'].widget.attrs['rows'] = 4