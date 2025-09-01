import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class QRCode(models.Model):
    """
    QR Code model for tracking all generated QR codes in the system.
    """
    class QRType(models.TextChoices):
        PRODUCT = 'product', _('Ürün')
        WAREHOUSE = 'warehouse', _('Depo')
        CORRIDOR = 'corridor', _('Koridor')
        CELL = 'cell', _('Hücre')
        SHOP = 'shop', _('Mağaza')
        BRAND = 'brand', _('Marka')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    qr_type = models.CharField(
        max_length=20,
        choices=QRType.choices,
        verbose_name=_('QR Türü')
    )
    
    # Generic foreign key fields
    object_id = models.CharField(
        max_length=255,
        verbose_name=_('Nesne ID')
    )
    
    # QR Code data
    qr_data = models.TextField(
        verbose_name=_('QR Veri'),
        help_text=_('QR kodunda saklanan veri')
    )
    
    qr_image = models.ImageField(
        upload_to='qr_codes/',
        verbose_name=_('QR Resmi')
    )
    
    # Additional information
    title = models.CharField(
        max_length=200,
        verbose_name=_('Başlık')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Access control
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='qr_codes',
        verbose_name=_('Marka')
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_qr_codes',
        verbose_name=_('Oluşturan')
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
        verbose_name = _('QR Kod')
        verbose_name_plural = _('QR Kodlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_qr_type_display()} - {self.title}"

    def get_absolute_url(self):
        return reverse('qr_codes:detail', kwargs={'pk': self.pk})

    def get_scan_url(self):
        """Get URL for scanning this QR code."""
        return reverse('qr_codes:scan', kwargs={'pk': self.pk})

    @classmethod
    def generate_for_product(cls, product, user=None):
        """Generate QR code for a product."""
        import qrcode
        from django.core.files.base import ContentFile
        from django.conf import settings
        from io import BytesIO
        
        # Create QR data
        qr_data = f"{settings.SITE_URL}/product/{product.slug}/"
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create QR code record
        qr_code = cls.objects.create(
            qr_type=cls.QRType.PRODUCT,
            object_id=str(product.id),
            qr_data=qr_data,
            title=product.name,
            description=f"QR kod: {product.name} ({product.sku})",
            brand=product.brand,
            created_by=user
        )
        
        # Save image
        filename = f"product_qr_{product.sku}.png"
        qr_code.qr_image.save(filename, ContentFile(buffer.read()), save=True)
        
        return qr_code

    @classmethod
    def generate_for_location(cls, location_type, location_obj, user=None):
        """Generate QR code for warehouse locations."""
        import qrcode
        from django.core.files.base import ContentFile
        from django.conf import settings
        from io import BytesIO
        
        # Determine QR data based on location type
        if location_type == 'warehouse':
            qr_data = f"{settings.SITE_URL}/warehouse/{location_obj.pk}/"
            title = location_obj.name
            brand = location_obj.shop.brand
        elif location_type == 'corridor':
            qr_data = f"{settings.SITE_URL}/corridor/{location_obj.pk}/"
            title = f"{location_obj.warehouse.name} - {location_obj.name}"
            brand = location_obj.warehouse.shop.brand
        elif location_type == 'cell':
            qr_data = f"{settings.SITE_URL}/cell/{location_obj.pk}/"
            title = location_obj.full_location
            brand = location_obj.corridor.warehouse.shop.brand
        else:
            raise ValueError("Invalid location type")
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create QR code record
        qr_code = cls.objects.create(
            qr_type=getattr(cls.QRType, location_type.upper()),
            object_id=str(location_obj.pk),
            qr_data=qr_data,
            title=title,
            description=f"Konum QR kodu: {title}",
            brand=brand,
            created_by=user
        )
        
        # Save image
        filename = f"{location_type}_qr_{location_obj.pk}.png"
        qr_code.qr_image.save(filename, ContentFile(buffer.read()), save=True)
        
        return qr_code


class QRScan(models.Model):
    """
    Track QR code scans for analytics and audit purposes.
    """
    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scans',
        verbose_name=_('QR Kod')
    )
    
    scanned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_scans',
        verbose_name=_('Tarayan')
    )
    
    # Device and location info
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Tarayıcı Bilgisi')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Adresi')
    )
    
    # GPS location of scan (if available)
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
    
    # Additional context
    scan_context = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Tarama Bağlamı'),
        help_text=_('Taramanın yapıldığı bağlam (örn: inventory, pickup, delivery)')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notlar')
    )
    
    scanned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Tarama Tarihi')
    )

    class Meta:
        verbose_name = _('QR Tarama')
        verbose_name_plural = _('QR Taramalar')
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.qr_code.title} - {self.scanned_at}"

    @property
    def scan_location(self):
        """Get formatted scan location."""
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return None


class QRPrintJob(models.Model):
    """
    Track QR code print jobs for inventory management.
    """
    class PrintStatus(models.TextChoices):
        PENDING = 'pending', _('Beklemede')
        PRINTING = 'printing', _('Yazdırılıyor')
        COMPLETED = 'completed', _('Tamamlandı')
        FAILED = 'failed', _('Başarısız')
        CANCELLED = 'cancelled', _('İptal Edildi')
    
    class PrintFormat(models.TextChoices):
        LABEL = 'label', _('Etiket')
        A4 = 'a4', _('A4 Sayfa')
        THERMAL = 'thermal', _('Termal Yazıcı')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    qr_codes = models.ManyToManyField(
        QRCode,
        related_name='print_jobs',
        verbose_name=_('QR Kodlar')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Yazdırma İşi Başlığı')
    )
    
    print_format = models.CharField(
        max_length=20,
        choices=PrintFormat.choices,
        default=PrintFormat.LABEL,
        verbose_name=_('Yazdırma Formatı')
    )
    
    copies = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Kopya Sayısı')
    )
    
    status = models.CharField(
        max_length=20,
        choices=PrintStatus.choices,
        default=PrintStatus.PENDING,
        verbose_name=_('Durum')
    )
    
    # User who created the print job
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='print_jobs',
        verbose_name=_('Oluşturan')
    )
    
    # Brand for access control
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='print_jobs',
        verbose_name=_('Marka')
    )
    
    # Print settings as JSON
    print_settings = models.JSONField(
        default=dict,
        verbose_name=_('Yazdırma Ayarları'),
        help_text=_('Yazdırma ayarları JSON formatında')
    )
    
    # Error information
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Hata Mesajı')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Başlama Tarihi')
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Tamamlanma Tarihi')
    )

    class Meta:
        verbose_name = _('QR Yazdırma İşi')
        verbose_name_plural = _('QR Yazdırma İşleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse('qr_codes:print_job_detail', kwargs={'pk': self.pk})

    @property
    def total_qr_codes(self):
        """Return total number of QR codes in this print job."""
        return self.qr_codes.count()

    @property
    def estimated_pages(self):
        """Calculate estimated pages based on format and copies."""
        total_items = self.total_qr_codes * self.copies
        
        if self.print_format == self.PrintFormat.LABEL:
            # Assume 8 labels per page
            return (total_items + 7) // 8
        elif self.print_format == self.PrintFormat.THERMAL:
            # Each QR code on separate thermal label
            return total_items
        else:  # A4
            # Assume 4 QR codes per A4 page
            return (total_items + 3) // 4

    def mark_as_started(self):
        """Mark print job as started."""
        from django.utils import timezone
        self.status = self.PrintStatus.PRINTING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_as_completed(self):
        """Mark print job as completed."""
        from django.utils import timezone
        self.status = self.PrintStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_as_failed(self, error_message=None):
        """Mark print job as failed."""
        self.status = self.PrintStatus.FAILED
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
