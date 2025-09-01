from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Brand, BrandSettings


class BrandSettingsInline(admin.StackedInline):
    """Inline for brand settings."""
    model = BrandSettings
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Brand admin interface."""
    
    list_display = ('name', 'slug', 'email', 'city', 'is_active', 'total_shops', 'total_products', 'created_at')
    list_filter = ('is_active', 'city', 'country', 'created_at')
    search_fields = ('name', 'email', 'phone', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    fieldsets = (
        (_('Temel Bilgiler'), {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        (_('İletişim Bilgileri'), {
            'fields': ('email', 'phone', 'website')
        }),
        (_('Adres Bilgileri'), {
            'fields': ('address', 'city', 'country', 'postal_code')
        }),
        (_('Vergi Bilgileri'), {
            'fields': ('tax_number', 'tax_office')
        }),
        (_('Durum'), {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [BrandSettingsInline]
    
    def logo_display(self, obj):
        """Display brand logo in admin."""
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
                obj.logo.url
            )
        return "Logo Yok"
    logo_display.short_description = _('Logo')


@admin.register(BrandSettings)
class BrandSettingsAdmin(admin.ModelAdmin):
    """Brand Settings admin interface."""
    
    list_display = ('brand', 'currency', 'currency_symbol', 'default_corridor_count', 'default_cell_count')
    list_filter = ('currency', 'email_notifications', 'low_stock_alert')
    search_fields = ('brand__name',)
    
    fieldsets = (
        (_('Para Birimi'), {
            'fields': ('currency', 'currency_symbol')
        }),
        (_('Depo Ayarları'), {
            'fields': ('default_corridor_count', 'default_cell_count')
        }),
        (_('QR Kod Ayarları'), {
            'fields': ('qr_code_prefix',)
        }),
        (_('Bildirim Ayarları'), {
            'fields': ('email_notifications', 'low_stock_alert', 'low_stock_threshold')
        }),
        (_('Tema Ayarları'), {
            'fields': ('primary_color', 'secondary_color')
        }),
    )
