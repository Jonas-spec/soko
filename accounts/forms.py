from django import forms
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class UserRegisterForm(BaseUserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'location')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'location')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }