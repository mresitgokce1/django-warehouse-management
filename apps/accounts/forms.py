from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import User
from brands.models import Brand


class UserCreationForm(BaseUserCreationForm):
    """Custom user creation form."""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'brand', 'phone')
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Customize form based on current user role
        if self.current_user and not self.current_user.is_system_admin:
            # Brand admins can't create system admins and are limited to their brand
            role_choices = [
                (User.UserRole.BRAND_ADMIN, _('Marka Yöneticisi')),
                (User.UserRole.BRAND_PERSONNEL, _('Marka Personeli')),
            ]
            self.fields['role'].choices = role_choices
            self.fields['brand'].queryset = Brand.objects.filter(id=self.current_user.brand.id)
            self.fields['brand'].initial = self.current_user.brand
            self.fields['brand'].widget = forms.HiddenInput()
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email


class UserEditForm(forms.ModelForm):
    """Form for editing user information."""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'brand', 'phone', 'is_active')
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Customize form based on current user role
        if self.current_user and not self.current_user.is_system_admin:
            # Brand admins can't edit system admins and are limited to their brand
            role_choices = [
                (User.UserRole.BRAND_ADMIN, _('Marka Yöneticisi')),
                (User.UserRole.BRAND_PERSONNEL, _('Marka Personeli')),
            ]
            self.fields['role'].choices = role_choices
            self.fields['brand'].queryset = Brand.objects.filter(id=self.current_user.brand.id)
            self.fields['brand'].widget = forms.HiddenInput()
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email


class ProfileEditForm(forms.ModelForm):
    """Form for editing own profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_image')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name == 'profile_image':
                field.widget.attrs.update({'class': 'form-control-file'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email


class LoginForm(forms.Form):
    """Custom login form."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Kullanıcı adı'),
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Şifre')
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )