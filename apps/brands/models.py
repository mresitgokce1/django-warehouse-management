import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Brand(models.Model):
    """
    Brand model for multi-brand warehouse management system.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Marka Adı')
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('URL Slug')
    )
    
    logo = models.ImageField(
        upload_to='brand_logos/',
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Contact Information
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('E-posta')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefon')
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Web Sitesi')
    )
    
    # Address Information
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Adres')
    )
    
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Şehir')
    )
    
    country = models.CharField(
        max_length=50,
        default='Türkiye',
        verbose_name=_('Ülke')
    )
    
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('Posta Kodu')
    )
    
    # Tax Information
    tax_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Vergi Numarası')
    )
    
    tax_office = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Vergi Dairesi')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncelleme Tarihi')
    )

    class Meta:
        verbose_name = _('Marka')
        verbose_name_plural = _('Markalar')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('brands:detail', kwargs={'slug': self.slug})

    @property
    def total_shops(self):
        """Return total number of shops for this brand."""
        return self.shops.count()

    @property
    def total_products(self):
        """Return total number of products for this brand."""
        return self.products.count()

    @property
    def total_users(self):
        """Return total number of users for this brand."""
        return self.user_set.count()


class BrandSettings(models.Model):
    """
    Brand-specific settings and preferences.
    """
    brand = models.OneToOneField(
        Brand,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_('Marka')
    )
    
    # Currency Settings
    currency = models.CharField(
        max_length=3,
        default='TRY',
        verbose_name=_('Para Birimi')
    )
    
    currency_symbol = models.CharField(
        max_length=5,
        default='₺',
        verbose_name=_('Para Birimi Sembolü')
    )
    
    # Warehouse Settings
    default_corridor_count = models.PositiveIntegerField(
        default=5,
        verbose_name=_('Varsayılan Koridor Sayısı')
    )
    
    default_cell_count = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Varsayılan Hücre Sayısı')
    )
    
    # QR Code Settings
    qr_code_prefix = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('QR Kod Öneki'),
        help_text=_('QR kodlarının başına eklenecek önek')
    )
    
    # Notification Settings
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('E-posta Bildirimleri')
    )
    
    low_stock_alert = models.BooleanField(
        default=True,
        verbose_name=_('Düşük Stok Uyarısı')
    )
    
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Düşük Stok Eşiği')
    )
    
    # Theme Settings
    primary_color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_('Ana Renk'),
        help_text=_('Hex renk kodu (örn: #007bff)')
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name=_('İkincil Renk'),
        help_text=_('Hex renk kodu (örn: #6c757d)')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncelleme Tarihi')
    )

    class Meta:
        verbose_name = _('Marka Ayarları')
        verbose_name_plural = _('Marka Ayarları')

    def __str__(self):
        return f"{self.brand.name} - Ayarlar"
