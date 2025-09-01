import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Shop(models.Model):
    """
    Shop model for managing multiple shops per brand.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='shops',
        verbose_name=_('Marka')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Mağaza Adı')
    )
    
    slug = models.SlugField(
        max_length=100,
        verbose_name=_('URL Slug')
    )
    
    code = models.CharField(
        max_length=20,
        verbose_name=_('Mağaza Kodu'),
        help_text=_('Dahili mağaza kodu')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Location Information
    address = models.TextField(
        verbose_name=_('Adres')
    )
    
    city = models.CharField(
        max_length=50,
        verbose_name=_('Şehir')
    )
    
    district = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('İlçe')
    )
    
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('Posta Kodu')
    )
    
    country = models.CharField(
        max_length=50,
        default='Türkiye',
        verbose_name=_('Ülke')
    )
    
    # GPS Coordinates
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_('Enlem')
    )
    
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name=_('Boylam')
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefon')
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('E-posta')
    )
    
    # Shop Manager
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_shops',
        verbose_name=_('Mağaza Müdürü')
    )
    
    # Status and Settings
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    is_main_shop = models.BooleanField(
        default=False,
        verbose_name=_('Ana Mağaza')
    )
    
    opening_hours = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Çalışma Saatleri'),
        help_text=_('JSON formatında saklanan çalışma saatleri')
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
        verbose_name = _('Mağaza')
        verbose_name_plural = _('Mağazalar')
        ordering = ['name']
        unique_together = [['brand', 'code'], ['brand', 'slug']]

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('shops:detail', kwargs={'slug': self.slug})

    @property
    def total_warehouses(self):
        """Return total number of warehouses for this shop."""
        return self.warehouses.count()

    @property
    def total_staff(self):
        """Return total number of staff assigned to this shop."""
        return self.staff.count()

    @property
    def address_display(self):
        """Return formatted address for display."""
        parts = [self.address]
        if self.district:
            parts.append(self.district)
        parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)


class ShopStaff(models.Model):
    """
    Staff assignment to shops.
    """
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='staff',
        verbose_name=_('Mağaza')
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='shop_assignments',
        verbose_name=_('Kullanıcı')
    )
    
    position = models.CharField(
        max_length=100,
        verbose_name=_('Pozisyon'),
        help_text=_('Mağazadaki pozisyonu (örn: Satış Danışmanı, Kasiyer)')
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Birincil Mağaza'),
        help_text=_('Bu kullanıcının ana çalıştığı mağaza mı?')
    )
    
    start_date = models.DateField(
        verbose_name=_('Başlama Tarihi')
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Bitiş Tarihi')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
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
        verbose_name = _('Mağaza Personeli')
        verbose_name_plural = _('Mağaza Personelleri')
        ordering = ['-created_at']
        unique_together = ['shop', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.shop.name} ({self.position})"

    @property
    def is_current_staff(self):
        """Check if staff assignment is currently active."""
        if not self.is_active:
            return False
        if self.end_date:
            from django.utils import timezone
            return self.end_date >= timezone.now().date()
        return True


class ShopInventory(models.Model):
    """
    Track inventory levels for each shop.
    """
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name=_('Mağaza')
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='shop_inventory',
        verbose_name=_('Ürün')
    )
    
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Miktar')
    )
    
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Rezerve Miktar'),
        help_text=_('Siparişlerde rezerve edilen miktar')
    )
    
    min_stock_level = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Minimum Stok Seviyesi')
    )
    
    max_stock_level = models.PositiveIntegerField(
        default=1000,
        verbose_name=_('Maksimum Stok Seviyesi')
    )
    
    last_restocked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Son Stok Yenileme')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncelleme Tarihi')
    )

    class Meta:
        verbose_name = _('Mağaza Envanteri')
        verbose_name_plural = _('Mağaza Envanterleri')
        unique_together = ['shop', 'product']
        ordering = ['product__name']

    def __str__(self):
        return f"{self.shop.name} - {self.product.name} ({self.quantity})"

    @property
    def available_quantity(self):
        """Return available quantity (total - reserved)."""
        return self.quantity - self.reserved_quantity

    @property
    def is_low_stock(self):
        """Check if inventory is low on stock."""
        return self.quantity <= self.min_stock_level

    @property
    def stock_status(self):
        """Get stock status as string."""
        if self.quantity == 0:
            return _('Stokta Yok')
        elif self.is_low_stock:
            return _('Düşük Stok')
        return _('Stokta Var')
