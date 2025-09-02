from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q, Count, F
from django.utils.translation import gettext_lazy as _

from .models import User, UserPermission
from .forms import UserCreationForm, UserEditForm, ProfileEditForm
from brands.models import Brand


class BrandAccessMixin(UserPassesTestMixin):
    """Mixin to ensure users can only access their brand's data."""
    
    def test_func(self):
        user = self.request.user
        if user.is_system_admin:
            return True
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if hasattr(obj, 'brand'):
                return user.has_brand_access(obj.brand)
        return True


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with role-based content."""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_system_admin:
            # System Admin Dashboard
            context.update({
                'total_brands': Brand.objects.count(),
                'total_users': User.objects.count(),
                'recent_brands': Brand.objects.order_by('-created_at')[:5],
                'recent_users': User.objects.order_by('-created_at')[:10],
            })
        elif user.is_brand_admin:
            # Brand Admin Dashboard
            brand = user.brand
            if brand:
                context.update({
                    'brand': brand,
                    'total_shops': brand.shops.count(),
                    'total_products': brand.products.count(),
                    'total_users': User.objects.filter(brand=brand).count(),
                    'recent_products': brand.products.order_by('-created_at')[:5],
                    'low_stock_products': brand.products.filter(
                        stock_quantity__lte=F('min_stock_level')
                    )[:5],
                })
            else:
                # Brand admin without assigned brand - show empty data
                context.update({
                    'brand': None,
                    'total_shops': 0,
                    'total_products': 0,
                    'total_users': 0,
                    'recent_products': [],
                    'low_stock_products': [],
                })
        else:
            # Brand Personnel Dashboard
            brand = user.brand
            if brand:
                context.update({
                    'brand': brand,
                    'my_permissions': user.custom_permissions.all(),
                    'recent_scans': user.qr_scans.order_by('-scanned_at')[:10],
                })
            else:
                # Personnel without assigned brand - show empty data
                context.update({
                    'brand': None,
                    'my_permissions': [],
                    'recent_scans': [],
                })
        
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view."""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile."""
    model = User
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Profil başarıyla güncellendi.'))
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, BrandAccessMixin, ListView):
    """List users (Brand Admin only)."""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.select_related('brand')
        
        if user.is_system_admin:
            pass  # System admin can see all users
        else:
            queryset = queryset.filter(brand=user.brand)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Role filter
        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['user_roles'] = User.UserRole.choices
        return context


class UserCreateView(LoginRequiredMixin, CreateView):
    """Create new user (Brand Admin only)."""
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_create.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_brand_admin or self.request.user.is_system_admin
    
    def form_valid(self, form):
        user = form.save(commit=False)
        if not self.request.user.is_system_admin:
            user.brand = self.request.user.brand
        user.save()
        messages.success(self.request, _('Kullanıcı başarıyla oluşturuldu.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs


class UserDetailView(LoginRequiredMixin, BrandAccessMixin, DetailView):
    """User detail view."""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['permissions'] = user.custom_permissions.all()
        context['recent_scans'] = user.qr_scans.order_by('-scanned_at')[:10]
        return context


class UserEditView(LoginRequiredMixin, BrandAccessMixin, UpdateView):
    """Edit user (Brand Admin only)."""
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_edit.html'
    
    def test_func(self):
        user = self.request.user
        if user.is_system_admin:
            return True
        if user.is_brand_admin:
            target_user = self.get_object()
            return user.brand == target_user.brand
        return False
    
    def get_success_url(self):
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Kullanıcı bilgileri başarıyla güncellendi.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs


class UserPermissionsView(LoginRequiredMixin, BrandAccessMixin, TemplateView):
    """Manage user permissions (Brand Admin only)."""
    template_name = 'accounts/user_permissions.html'
    
    def test_func(self):
        user = self.request.user
        if user.is_brand_admin:
            target_user = get_object_or_404(User, pk=self.kwargs['pk'])
            return user.brand == target_user.brand
        return user.is_system_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = get_object_or_404(User, pk=self.kwargs['pk'])
        context['target_user'] = target_user
        context['available_permissions'] = UserPermission.PermissionType.choices
        context['current_permissions'] = target_user.custom_permissions.values_list('permission', flat=True)
        return context
    
    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, pk=self.kwargs['pk'])
        selected_permissions = request.POST.getlist('permissions')
        
        # Remove old permissions
        target_user.custom_permissions.all().delete()
        
        # Add new permissions
        for permission in selected_permissions:
            UserPermission.objects.create(
                user=target_user,
                permission=permission,
                granted_by=request.user
            )
        
        messages.success(request, _('Kullanıcı izinleri başarıyla güncellendi.'))
        return redirect('accounts:user_detail', pk=target_user.pk)


@login_required
def toggle_user_status(request):
    """Ajax endpoint to toggle user active status."""
    if request.method == 'POST' and request.user.is_brand_admin:
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            if request.user.has_brand_access(user.brand):
                user.is_active = not user.is_active
                user.save()
                return JsonResponse({
                    'success': True,
                    'new_status': user.is_active,
                    'message': _('Kullanıcı durumu güncellendi.')
                })
        except User.DoesNotExist:
            pass
    
    return JsonResponse({
        'success': False,
        'message': _('İşlem başarısız oldu.')
    })
