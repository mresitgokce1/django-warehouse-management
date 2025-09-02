from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import QRCode, QRScan, QRPrintJob
from accounts.views import BrandAccessMixin


class QRScannerView(LoginRequiredMixin, TemplateView):
    """QR code scanner interface."""
    template_name = 'qr_codes/scanner.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent scans by the user
        context['recent_scans'] = QRScan.objects.filter(
            scanned_by=user
        ).select_related('qr_code').order_by('-scanned_at')[:10]
        
        return context


class QRPrintView(LoginRequiredMixin, BrandAccessMixin, TemplateView):
    """QR code printing interface."""
    template_name = 'qr_codes/print.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get available QR codes for printing
        if user.is_system_admin:
            qr_codes = QRCode.objects.filter(is_active=True)
        else:
            qr_codes = QRCode.objects.filter(
                brand=user.brand,
                is_active=True
            )
        
        # Get recent print jobs
        if user.is_system_admin:
            print_jobs = QRPrintJob.objects.all()
        else:
            print_jobs = QRPrintJob.objects.filter(brand=user.brand)
        
        context['qr_codes'] = qr_codes.order_by('-created_at')[:50]
        context['recent_print_jobs'] = print_jobs.order_by('-created_at')[:10]
        context['print_formats'] = QRPrintJob.PrintFormat.choices
        
        return context
