from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import User, UserPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface."""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'brand', 'is_active', 'created_at')
    list_filter = ('role', 'brand', 'is_active', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_image')}),
        (_('Rol ve Marka'), {'fields': ('role', 'brand')}),
        (_('İzinler'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Önemli Tarihler'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'brand'),
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            # Brand admins can only see users from their brand
            if hasattr(request.user, 'brand') and request.user.brand:
                queryset = queryset.filter(brand=request.user.brand)
        return queryset


class UserPermissionInline(admin.TabularInline):
    """Inline for user permissions."""
    model = UserPermission
    extra = 0
    fk_name = 'user'


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """User Permission admin interface."""
    
    list_display = ('user', 'permission', 'granted_by', 'created_at')
    list_filter = ('permission', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            # Brand admins can only see permissions for their brand users
            if hasattr(request.user, 'brand') and request.user.brand:
                queryset = queryset.filter(user__brand=request.user.brand)
        return queryset
