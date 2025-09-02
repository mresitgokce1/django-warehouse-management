from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Shop, ShopStaff, ShopInventory
from accounts.views import BrandAccessMixin


class ShopListView(LoginRequiredMixin, BrandAccessMixin, ListView):
    """List all shops for the user's brand."""
    model = Shop
    template_name = 'shops/shop_list.html'
    context_object_name = 'shops'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Shop.objects.select_related('brand', 'manager')
        
        if user.is_system_admin:
            pass  # System admin can see all shops
        else:
            queryset = queryset.filter(brand=user.brand)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class StaffManagementView(LoginRequiredMixin, BrandAccessMixin, TemplateView):
    """Manage staff assignments across shops."""
    template_name = 'shops/staff_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_system_admin:
            staff_assignments = ShopStaff.objects.select_related(
                'shop', 'user', 'shop__brand'
            ).all()
        else:
            staff_assignments = ShopStaff.objects.select_related(
                'shop', 'user'
            ).filter(shop__brand=user.brand)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            staff_assignments = staff_assignments.filter(
                user__username__icontains=search_query
            )
        
        context['staff_assignments'] = staff_assignments.order_by('-created_at')
        context['search_query'] = self.request.GET.get('search', '')
        return context
