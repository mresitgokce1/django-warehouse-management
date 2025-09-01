from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based permissions and brand association.
    """
    
    class UserRole(models.TextChoices):
        SYSTEM_ADMIN = 'system_admin', _('Sistem Yöneticisi')
        BRAND_ADMIN = 'brand_admin', _('Marka Yöneticisi')  
        BRAND_PERSONNEL = 'brand_personnel', _('Marka Personeli')
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.BRAND_PERSONNEL,
        verbose_name=_('Rol')
    )
    
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Marka'),
        help_text=_('System Admin için boş bırakılabilir')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefon')
    )
    
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name=_('Profil Resmi')
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
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    @property
    def is_system_admin(self):
        """Check if user is a system admin."""
        return self.role == self.UserRole.SYSTEM_ADMIN

    @property
    def is_brand_admin(self):
        """Check if user is a brand admin."""
        return self.role == self.UserRole.BRAND_ADMIN

    @property
    def is_brand_personnel(self):
        """Check if user is brand personnel."""
        return self.role == self.UserRole.BRAND_PERSONNEL

    def has_brand_access(self, brand):
        """Check if user has access to a specific brand."""
        if self.is_system_admin:
            return True
        return self.brand == brand

    def get_accessible_brands(self):
        """Get brands accessible by this user."""
        if self.is_system_admin:
            from brands.models import Brand
            return Brand.objects.all()
        elif self.brand:
            return [self.brand]
        return []


class UserPermission(models.Model):
    """
    Additional permissions for brand personnel.
    """
    
    class PermissionType(models.TextChoices):
        VIEW_PRODUCTS = 'view_products', _('Ürünleri Görüntüle')
        MANAGE_PRODUCTS = 'manage_products', _('Ürünleri Yönet')
        VIEW_STOCK = 'view_stock', _('Stok Görüntüle')
        MANAGE_STOCK = 'manage_stock', _('Stok Yönet')
        VIEW_WAREHOUSES = 'view_warehouses', _('Depoları Görüntüle')
        MANAGE_WAREHOUSES = 'manage_warehouses', _('Depoları Yönet')
        VIEW_SHOPS = 'view_shops', _('Mağazaları Görüntüle')
        MANAGE_SHOPS = 'manage_shops', _('Mağazaları Yönet')
        VIEW_REPORTS = 'view_reports', _('Raporları Görüntüle')
        GENERATE_QR = 'generate_qr', _('QR Kod Oluştur')
        SCAN_QR = 'scan_qr', _('QR Kod Tara')
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_permissions',
        verbose_name=_('Kullanıcı')
    )
    
    permission = models.CharField(
        max_length=30,
        choices=PermissionType.choices,
        verbose_name=_('İzin')
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='granted_permissions',
        verbose_name=_('İzin Veren')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturma Tarihi')
    )

    class Meta:
        verbose_name = _('Kullanıcı İzni')
        verbose_name_plural = _('Kullanıcı İzinleri')
        unique_together = ['user', 'permission']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_permission_display()}"
