import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from PIL import Image
import os


class Category(models.Model):
    """
    Product category model with hierarchical support.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('Marka')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Kategori Adı')
    )
    
    slug = models.SlugField(
        max_length=100,
        verbose_name=_('URL Slug')
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Üst Kategori')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True,
        verbose_name=_('Kategori Resmi')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Sıralama')
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
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategoriler')
        ordering = ['order', 'name']
        unique_together = ['brand', 'slug']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        """Return number of products in this category."""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Main product model with comprehensive features.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Marka')
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Kategori')
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Ürün Adı')
    )
    
    slug = models.SlugField(
        max_length=200,
        verbose_name=_('URL Slug')
    )
    
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('SKU Kodu'),
        help_text=_('Stok Tutma Birimi')
    )
    
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Barkod')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    short_description = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Kısa Açıklama')
    )
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Maliyet Fiyatı')
    )
    
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Satış Fiyatı')
    )
    
    # Stock Information
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Stok Miktarı')
    )
    
    min_stock_level = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Minimum Stok Seviyesi')
    )
    
    max_stock_level = models.PositiveIntegerField(
        default=1000,
        verbose_name=_('Maksimum Stok Seviyesi')
    )
    
    # Physical Properties
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_('Ağırlık (kg)')
    )
    
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Uzunluk (cm)')
    )
    
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Genişlik (cm)')
    )
    
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Yükseklik (cm)')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Öne Çıkan')
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to='product_qr_codes/',
        blank=True,
        null=True,
        verbose_name=_('QR Kod')
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
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')
        ordering = ['-created_at']
        unique_together = ['brand', 'slug']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def is_low_stock(self):
        """Check if product is low on stock."""
        return self.stock_quantity <= self.min_stock_level

    @property
    def stock_status(self):
        """Get stock status as string."""
        if self.stock_quantity == 0:
            return _('Stokta Yok')
        elif self.is_low_stock:
            return _('Düşük Stok')
        return _('Stokta Var')

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost_price and self.selling_price:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

    def save(self, *args, **kwargs):
        """Override save to generate QR code."""
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()

    def generate_qr_code(self):
        """Generate QR code for the product."""
        import qrcode
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_data = f"{self.brand.slug}/product/{self.slug}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model
        filename = f"qr_code_{self.sku}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        super().save(update_fields=['qr_code'])


class ProductImage(models.Model):
    """
    Product image gallery.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Ürün')
    )
    
    image = models.ImageField(
        upload_to='product_images/',
        verbose_name=_('Ürün Resmi')
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Alt Metin')
    )
    
    is_main = models.BooleanField(
        default=False,
        verbose_name=_('Ana Resim')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Sıralama')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )

    class Meta:
        verbose_name = _('Ürün Resmi')
        verbose_name_plural = _('Ürün Resimleri')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.product.name} - Resim {self.order}"

    def save(self, *args, **kwargs):
        """Override save to resize image."""
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(self.image.path)


class StockMovement(models.Model):
    """
    Track stock movements for products.
    """
    class MovementType(models.TextChoices):
        IN = 'in', _('Giriş')
        OUT = 'out', _('Çıkış')
        ADJUSTMENT = 'adjustment', _('Düzeltme')
        RETURN = 'return', _('İade')
        DAMAGE = 'damage', _('Hasar')
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name=_('Ürün')
    )
    
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        verbose_name=_('Hareket Türü')
    )
    
    quantity = models.IntegerField(
        verbose_name=_('Miktar'),
        help_text=_('Pozitif değer: artış, Negatif değer: azalış')
    )
    
    previous_stock = models.PositiveIntegerField(
        verbose_name=_('Önceki Stok')
    )
    
    new_stock = models.PositiveIntegerField(
        verbose_name=_('Yeni Stok')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notlar')
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Kullanıcı')
    )
    
    warehouse_location = models.ForeignKey(
        'warehouses.Cell',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Depo Konumu')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )

    class Meta:
        verbose_name = _('Stok Hareketi')
        verbose_name_plural = _('Stok Hareketleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
