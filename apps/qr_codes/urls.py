from django.urls import path

from . import views

app_name = 'qr_codes'

urlpatterns = [
    # QR Code functionality
    path('scanner/', views.QRScannerView.as_view(), name='scanner'),
    path('print/', views.QRPrintView.as_view(), name='print'),
]