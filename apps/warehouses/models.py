import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Warehouse(models.Model):
    """
    Warehouse model for managing storage facilities.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='warehouses',
        verbose_name=_('Mağaza')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Depo Adı')
    )
    
    code = models.CharField(
        max_length=20,
        verbose_name=_('Depo Kodu')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Location Information
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Adres')
    )
    
    # Physical Properties
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Toplam Alan (m²)')
    )
    
    usable_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Kullanılabilir Alan (m²)')
    )
    
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Yükseklik (m)')
    )
    
    # Capacity Settings
    corridor_count = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name=_('Koridor Sayısı')
    )
    
    # Temperature Settings
    temperature_controlled = models.BooleanField(
        default=False,
        verbose_name=_('Sıcaklık Kontrollü')
    )
    
    min_temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Minimum Sıcaklık (°C)')
    )
    
    max_temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maksimum Sıcaklık (°C)')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    # QR Code for warehouse
    qr_code = models.ImageField(
        upload_to='warehouse_qr_codes/',
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
        verbose_name = _('Depo')
        verbose_name_plural = _('Depolar')
        ordering = ['name']
        unique_together = [['shop', 'code']]

    def __str__(self):
        return f"{self.shop.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('warehouses:detail', kwargs={'pk': self.pk})

    @property
    def total_corridors(self):
        """Return total number of corridors."""
        return self.corridors.count()

    @property
    def total_cells(self):
        """Return total number of cells across all corridors."""
        return sum(corridor.cells.count() for corridor in self.corridors.all())

    @property
    def occupied_cells(self):
        """Return number of occupied cells."""
        return sum(corridor.occupied_cells for corridor in self.corridors.all())

    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage."""
        total = self.total_cells
        if total == 0:
            return 0
        return (self.occupied_cells / total) * 100

    def save(self, *args, **kwargs):
        """Override save to generate QR code and corridors."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Generate QR code
            self.generate_qr_code()
            # Create default corridors
            self.create_default_corridors()

    def generate_qr_code(self):
        """Generate QR code for the warehouse."""
        import qrcode
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_data = f"warehouse/{self.pk}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"warehouse_qr_{self.code}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        super().save(update_fields=['qr_code'])

    def create_default_corridors(self):
        """Create default corridors for the warehouse."""
        for i in range(1, self.corridor_count + 1):
            Corridor.objects.create(
                warehouse=self,
                number=i,
                name=f"Koridor {i}"
            )


class Corridor(models.Model):
    """
    Corridor model for warehouse organization.
    """
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='corridors',
        verbose_name=_('Depo')
    )
    
    number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_('Koridor Numarası')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Koridor Adı')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Cell Settings
    cell_count = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_('Hücre Sayısı')
    )
    
    # Physical Properties
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Uzunluk (m)')
    )
    
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Genişlik (m)')
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
        verbose_name = _('Koridor')
        verbose_name_plural = _('Koridorlar')
        ordering = ['number']
        unique_together = ['warehouse', 'number']

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"

    @property
    def occupied_cells(self):
        """Return number of occupied cells in this corridor."""
        return self.cells.filter(is_occupied=True).count()

    @property
    def available_cells(self):
        """Return number of available cells in this corridor."""
        return self.cells.filter(is_occupied=False).count()

    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage."""
        total = self.cells.count()
        if total == 0:
            return 0
        return (self.occupied_cells / total) * 100

    def save(self, *args, **kwargs):
        """Override save to create default cells."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.create_default_cells()

    def create_default_cells(self):
        """Create default cells for the corridor."""
        for i in range(1, self.cell_count + 1):
            Cell.objects.create(
                corridor=self,
                number=i,
                name=f"Hücre {i}"
            )


class Cell(models.Model):
    """
    Storage cell model for detailed location tracking.
    """
    corridor = models.ForeignKey(
        Corridor,
        on_delete=models.CASCADE,
        related_name='cells',
        verbose_name=_('Koridor')
    )
    
    number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name=_('Hücre Numarası')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Hücre Adı')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    
    # Physical Properties
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Uzunluk (cm)')
    )
    
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Genişlik (cm)')
    )
    
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Yükseklik (cm)')
    )
    
    # Capacity
    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maksimum Ağırlık (kg)')
    )
    
    max_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maksimum Hacim (cm³)')
    )
    
    # Status
    is_occupied = models.BooleanField(
        default=False,
        verbose_name=_('Dolu')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif')
    )
    
    is_reserved = models.BooleanField(
        default=False,
        verbose_name=_('Rezerve')
    )
    
    # QR Code for cell navigation
    qr_code = models.ImageField(
        upload_to='cell_qr_codes/',
        blank=True,
        null=True,
        verbose_name=_('QR Kod')
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
        verbose_name = _('Hücre')
        verbose_name_plural = _('Hücreler')
        ordering = ['number']
        unique_together = ['corridor', 'number']

    def __str__(self):
        return f"{self.corridor.warehouse.name} - {self.corridor.name} - {self.name}"

    @property
    def full_location(self):
        """Return full location path."""
        return f"{self.corridor.warehouse.name} > {self.corridor.name} > {self.name}"

    @property
    def location_code(self):
        """Return standardized location code."""
        return f"W{self.corridor.warehouse.code}-C{self.corridor.number:02d}-H{self.number:03d}"

    def save(self, *args, **kwargs):
        """Override save to generate QR code."""
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()

    def generate_qr_code(self):
        """Generate QR code for the cell."""
        import qrcode
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_data = f"cell/{self.pk}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"cell_qr_{self.location_code}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        super().save(update_fields=['qr_code'])


class ProductLocation(models.Model):
    """
    Track product locations within warehouse cells.
    """
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_('Ürün')
    )
    
    cell = models.ForeignKey(
        Cell,
        on_delete=models.CASCADE,
        related_name='stored_products',
        verbose_name=_('Hücre')
    )
    
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Miktar')
    )
    
    # Position within cell
    position_notes = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Pozisyon Notları'),
        help_text=_('Hücre içindeki konum bilgisi')
    )
    
    # Placement details
    placed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='placed_products',
        verbose_name=_('Yerleştiren')
    )
    
    placed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yerleştirilme Tarihi')
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Son Güncelleme')
    )
    
    # Optional expiry tracking
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Son Kullanma Tarihi')
    )
    
    batch_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parti Numarası')
    )

    class Meta:
        verbose_name = _('Ürün Konumu')
        verbose_name_plural = _('Ürün Konumları')
        ordering = ['-placed_at']
        unique_together = ['product', 'cell', 'batch_number']

    def __str__(self):
        return f"{self.product.name} - {self.cell.full_location} ({self.quantity})"

    @property
    def is_expired(self):
        """Check if product has expired."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()

    @property
    def days_to_expiry(self):
        """Calculate days until expiry."""
        if not self.expiry_date:
            return None
        from django.utils import timezone
        delta = self.expiry_date - timezone.now().date()
        return delta.days
