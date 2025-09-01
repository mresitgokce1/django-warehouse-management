from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Product creation and editing form."""
    
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'sku', 'barcode', 'description', 'short_description',
            'cost_price', 'selling_price', 'stock_quantity', 'min_stock_level', 
            'max_stock_level', 'weight', 'length', 'width', 'height',
            'is_active', 'is_featured'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ürün adı')
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SKU kodu')
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Barkod (opsiyonel)')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Detaylı ürün açıklaması')
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Kısa açıklama')
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'min_stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'max_stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories by user's brand
        if self.user and not self.user.is_system_admin:
            self.fields['category'].queryset = Category.objects.filter(
                brand=self.user.brand, 
                is_active=True
            )
    
    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if sku:
            sku = sku.upper().strip()
            # Check for duplicate SKU
            queryset = Product.objects.filter(sku=sku)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(_('Bu SKU kodu zaten kullanılıyor.'))
        
        return sku
    
    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        if barcode:
            barcode = barcode.strip()
            # Check for duplicate barcode
            queryset = Product.objects.filter(barcode=barcode)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(_('Bu barkod zaten kullanılıyor.'))
        
        return barcode
    
    def clean(self):
        cleaned_data = super().clean()
        min_stock = cleaned_data.get('min_stock_level', 0)
        max_stock = cleaned_data.get('max_stock_level', 0)
        
        if min_stock and max_stock and min_stock >= max_stock:
            raise forms.ValidationError(
                _('Minimum stok seviyesi maksimum stok seviyesinden küçük olmalıdır.')
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        product = super().save(commit=False)
        
        # Generate slug from name
        if not product.slug or product.slug == slugify(product.name):
            product.slug = slugify(product.name)
            
            # Ensure unique slug only after brand is set
            if hasattr(product, 'brand') and product.brand:
                original_slug = product.slug
                counter = 1
                while Product.objects.filter(slug=product.slug, brand=product.brand).exclude(pk=product.pk).exists():
                    product.slug = f"{original_slug}-{counter}"
                    counter += 1
        
        if commit:
            product.save()
        
        return product


class CategoryForm(forms.ModelForm):
    """Category creation and editing form."""
    
    class Meta:
        model = Category
        fields = ['parent', 'name', 'description', 'image', 'is_active', 'order']
        
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Kategori adı')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Kategori açıklaması')
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter parent categories by user's brand
        if self.user and not self.user.is_system_admin:
            self.fields['parent'].queryset = Category.objects.filter(
                brand=self.user.brand,
                is_active=True
            )
            
        # Exclude self from parent options when editing
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(
                pk=self.instance.pk
            )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
        return name
    
    def save(self, commit=True):
        category = super().save(commit=False)
        
        # Generate slug from name
        if not category.slug or category.slug == slugify(category.name):
            category.slug = slugify(category.name)
            
            # Ensure unique slug within brand
            original_slug = category.slug
            counter = 1
            while Category.objects.filter(slug=category.slug, brand=category.brand).exclude(pk=category.pk).exists():
                category.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if commit:
            category.save()
        
        return category


class ProductSearchForm(forms.Form):
    """Product search form for advanced filtering."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ürün adı, SKU veya barkod ara...')
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label=_('Tüm kategoriler'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    stock_status = forms.ChoiceField(
        choices=[
            ('', _('Tüm stok durumları')),
            ('available', _('Stokta var')),
            ('low', _('Düşük stok')),
            ('out', _('Stokta yok')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    order_by = forms.ChoiceField(
        choices=[
            ('-created_at', _('En yeni')),
            ('created_at', _('En eski')),
            ('name', _('İsim (A-Z)')),
            ('-name', _('İsim (Z-A)')),
            ('-stock_quantity', _('Stok (Yüksek-Düşük)')),
            ('stock_quantity', _('Stok (Düşük-Yüksek)')),
            ('-selling_price', _('Fiyat (Yüksek-Düşük)')),
            ('selling_price', _('Fiyat (Düşük-Yüksek)')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    featured = forms.BooleanField(
        required=False,
        label=_('Sadece öne çıkanlar'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_inactive = forms.BooleanField(
        required=False,
        label=_('Pasif ürünleri göster'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_system_admin:
            self.fields['category'].queryset = Category.objects.filter(
                brand=user.brand,
                is_active=True
            )
        else:
            self.fields['category'].queryset = Category.objects.filter(is_active=True)