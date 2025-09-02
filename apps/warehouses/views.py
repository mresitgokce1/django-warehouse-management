from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Warehouse, Corridor, Cell, ProductLocation
from accounts.views import BrandAccessMixin


class WarehouseListView(LoginRequiredMixin, BrandAccessMixin, ListView):
    """List all warehouses for the user's brand."""
    model = Warehouse
    template_name = 'warehouses/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Warehouse.objects.select_related('shop', 'shop__brand')
        
        if user.is_system_admin:
            pass  # System admin can see all warehouses
        else:
            queryset = queryset.filter(shop__brand=user.brand)
        
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


class LocationManagementView(LoginRequiredMixin, BrandAccessMixin, TemplateView):
    """Manage warehouse locations (corridors and cells)."""
    template_name = 'warehouses/location_manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_system_admin:
            warehouses = Warehouse.objects.select_related('shop', 'shop__brand').all()
        else:
            warehouses = Warehouse.objects.select_related('shop').filter(shop__brand=user.brand)
        
        # Get warehouse details with corridors and cells
        warehouse_data = []
        for warehouse in warehouses:
            corridors = []
            for corridor in warehouse.corridors.all():
                corridors.append({
                    'corridor': corridor,
                    'cells': corridor.cells.all()[:10],  # Limit for performance
                    'total_cells': corridor.cells.count(),
                    'occupied_cells': corridor.occupied_cells,
                    'occupancy_rate': corridor.occupancy_rate,
                })
            
            warehouse_data.append({
                'warehouse': warehouse,
                'corridors': corridors,
                'total_corridors': warehouse.total_corridors,
                'total_cells': warehouse.total_cells,
                'occupied_cells': warehouse.occupied_cells,
                'occupancy_rate': warehouse.occupancy_rate,
            })
        
        context['warehouse_data'] = warehouse_data
        return context
