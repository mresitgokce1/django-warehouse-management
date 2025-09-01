"""
URL configuration for django_warehouse_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect


def home_redirect(request):
    """Redirect home page to appropriate dashboard based on user role."""
    if request.user.is_authenticated:
        if request.user.is_system_admin:
            return redirect('admin:index')
        else:
            return redirect('accounts:dashboard')
    return redirect('accounts:login')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home redirect
    path('', home_redirect, name='home'),
    
    # Authentication URLs
    path('accounts/', include('accounts.urls')),
    
    # App URLs
    path('brands/', include('brands.urls')),
    path('products/', include('products.urls')),
    path('shops/', include('shops.urls')),
    path('warehouses/', include('warehouses.urls')),
    path('qr-codes/', include('qr_codes.urls')),
    
    # API URLs
    path('api/v1/', include('api.urls')),
    
    # Built-in auth URLs for password reset, etc.
    path('auth/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
