from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from accounts.views import BrandAccessMixin
from .models import Product, Category, StockMovement
from .forms import ProductForm, CategoryForm


class ProductListView(LoginRequiredMixin, BrandAccessMixin, ListView):
    """List products with search and filtering."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.select_related('brand', 'category')
        
        # Filter by user's brand
        if not user.is_system_admin:
            queryset = queryset.filter(brand=user.brand)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(barcode__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Stock status filter
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'low':
            queryset = queryset.filter(stock_quantity__lte=F('min_stock_level'))
        elif stock_status == 'out':
            queryset = queryset.filter(stock_quantity=0)
        elif stock_status == 'available':
            queryset = queryset.filter(stock_quantity__gt=F('min_stock_level'))
        
        # Featured filter
        if self.request.GET.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        # Active filter
        if self.request.GET.get('show_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        
        # Ordering
        order_by = self.request.GET.get('order_by', '-created_at')
        if order_by in ['name', '-name', 'stock_quantity', '-stock_quantity', 
                       'selling_price', '-selling_price', 'created_at', '-created_at']:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get categories for filter
        if user.is_system_admin:
            categories = Category.objects.filter(is_active=True)
        else:
            categories = Category.objects.filter(brand=user.brand, is_active=True)
        
        context.update({
            'categories': categories,
            'search_query': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'stock_status': self.request.GET.get('stock_status', ''),
            'order_by': self.request.GET.get('order_by', '-created_at'),
            'show_inactive': self.request.GET.get('show_inactive', 'false'),
            'featured': self.request.GET.get('featured', ''),
        })
        return context


class ProductDetailView(LoginRequiredMixin, BrandAccessMixin, DetailView):
    """Product detail view with QR code and stock information."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get recent stock movements
        recent_movements = product.stock_movements.select_related('user', 'warehouse_location').order_by('-created_at')[:10]
        
        # Get product locations
        locations = product.locations.select_related('cell__corridor__warehouse').filter(quantity__gt=0)
        
        context.update({
            'recent_movements': recent_movements,
            'locations': locations,
            'images': product.images.all().order_by('order', '-created_at'),
            'main_image': product.images.filter(is_main=True).first(),
        })
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Create new product."""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def form_valid(self, form):
        product = form.save(commit=False)
        # Always set brand from current user
        product.brand = self.request.user.brand
        product.save()
        messages.success(self.request, _('Ürün başarıyla oluşturuldu.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ProductUpdateView(LoginRequiredMixin, BrandAccessMixin, UpdateView):
    """Update existing product."""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def form_valid(self, form):
        messages.success(self.request, _('Ürün başarıyla güncellendi.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ProductDeleteView(LoginRequiredMixin, BrandAccessMixin, DeleteView):
    """Delete product (soft delete by setting inactive)."""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Soft delete: set inactive instead of actual deletion
        self.object.is_active = False
        self.object.save()
        messages.success(request, _('Ürün başarıyla devre dışı bırakıldı.'))
        return redirect(self.success_url)


class CategoryListView(LoginRequiredMixin, BrandAccessMixin, ListView):
    """List product categories."""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.select_related('brand', 'parent')
        
        if not user.is_system_admin:
            queryset = queryset.filter(brand=user.brand)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Show only active by default
        if self.request.GET.get('show_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'show_inactive': self.request.GET.get('show_inactive', 'false'),
        })
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create new category."""
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def form_valid(self, form):
        category = form.save(commit=False)
        if not self.request.user.is_system_admin:
            category.brand = self.request.user.brand
        category.save()
        messages.success(self.request, _('Kategori başarıyla oluşturuldu.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CategoryUpdateView(LoginRequiredMixin, BrandAccessMixin, UpdateView):
    """Update category."""
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def form_valid(self, form):
        messages.success(self.request, _('Kategori başarıyla güncellendi.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
