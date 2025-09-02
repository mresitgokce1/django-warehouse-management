from django.urls import path

from . import views

app_name = 'shops'

urlpatterns = [
    # Shop management
    path('', views.ShopListView.as_view(), name='shop_list'),
    path('staff/', views.StaffManagementView.as_view(), name='staff_list'),
]