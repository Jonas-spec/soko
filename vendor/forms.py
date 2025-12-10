from django import forms
from django.contrib.auth.models import User
from .models import Vendor
from products.models import Product

# --- 1. THE MISSING REGISTRATION FORM ---
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
    # This is the field that lets them choose
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
        fields = ['username', 'email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # Style the standard fields
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password does not match"
            )

# --- 2. VENDOR PROFILE FORM (Refined) ---
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
        
        # Loop through all fields to apply 'form-control' 
        # (This is cleaner than writing them out manually one by one)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Determine if we need to style the file input differently
        if 'logo' in self.fields:
            self.fields['logo'].widget.attrs['class'] = 'form-control-file'

# --- 3. PRODUCT FORM (As you had it) ---
class ProductForm(forms.ModelForm):
    """
    Form for vendors to add or edit products.
    """
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
        # FIX: Pop 'vendor' from kwargs before calling super()
        # This prevents the 'unexpected keyword argument' error
        if 'vendor' in kwargs:
            kwargs.pop('vendor')
            
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Add Bootstrap classes for styling
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
        # Specific tweaks
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['description'].widget.attrs['rows'] = 4