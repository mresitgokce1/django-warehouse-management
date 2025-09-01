from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # Product URLs
    path('', views.ProductListView.as_view(), name='list'),
    path('create/', views.ProductCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
]