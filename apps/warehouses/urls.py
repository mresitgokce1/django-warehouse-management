from django.urls import path

from . import views

app_name = 'warehouses'

urlpatterns = [
    # Warehouse management
    path('', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('locations/', views.LocationManagementView.as_view(), name='location_manage'),
]