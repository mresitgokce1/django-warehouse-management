// Custom JavaScript for Django Warehouse Management System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    $('.alert:not(.alert-permanent)').delay(5000).fadeOut('slow');

    // Confirm delete actions
    $('.btn-delete').on('click', function(e) {
        if (!confirm('Bu işlemi gerçekleştirmek istediğinizden emin misiniz?')) {
            e.preventDefault();
        }
    });

    // Toggle user status
    $('.toggle-user-status').on('click', function(e) {
        e.preventDefault();
        const userId = $(this).data('user-id');
        const url = $(this).data('url');
        
        $.post(url, {
            'user_id': userId,
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        }, function(data) {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message);
            }
        });
    });

    // Search functionality
    $('.search-input').on('input', debounce(function() {
        const query = $(this).val();
        const form = $(this).closest('form');
        if (query.length >= 2 || query.length === 0) {
            form.submit();
        }
    }, 300));

    // QR Code Scanner (if device supports it)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        $('.qr-scanner-btn').show();
    }

    // Stock level warnings
    $('.stock-quantity').each(function() {
        const quantity = parseInt($(this).text());
        const minLevel = parseInt($(this).data('min-level'));
        
        if (quantity === 0) {
            $(this).addClass('text-danger').append(' <i class="bi bi-exclamation-triangle"></i>');
        } else if (quantity <= minLevel) {
            $(this).addClass('text-warning').append(' <i class="bi bi-exclamation-circle"></i>');
        }
    });

    // Warehouse cell interactions
    $('.cell').on('click', function() {
        const cellId = $(this).data('cell-id');
        const cellInfo = $(this).data('cell-info');
        
        // Show cell information in modal or sidebar
        showCellInfo(cellId, cellInfo);
    });

    // Auto-refresh dashboard data every 30 seconds
    if ($('.dashboard').length > 0) {
        setInterval(function() {
            refreshDashboardData();
        }, 30000);
    }
});

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showCellInfo(cellId, cellInfo) {
    // Implementation for showing cell information
    const modal = new bootstrap.Modal(document.getElementById('cellInfoModal'));
    $('#cellInfoModal .modal-body').html(cellInfo);
    modal.show();
}

function refreshDashboardData() {
    // Refresh dashboard statistics without full page reload
    $.get(window.location.href + '?ajax=1', function(data) {
        if (data.stats) {
            Object.keys(data.stats).forEach(function(key) {
                $(`[data-stat="${key}"]`).text(data.stats[key]);
            });
        }
    });
}

// QR Code Scanner
function startQRScanner(targetInput) {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
            .then(function(stream) {
                const video = document.getElementById('qr-scanner-video');
                video.srcObject = stream;
                video.play();
                
                // Show scanner modal
                const modal = new bootstrap.Modal(document.getElementById('qrScannerModal'));
                modal.show();
                
                // Start scanning
                scanQRCode(video, targetInput, stream);
            })
            .catch(function(err) {
                console.error('QR Scanner error:', err);
                alert('Kamera erişimi sağlanamadı.');
            });
    }
}

function scanQRCode(video, targetInput, stream) {
    // This would integrate with a QR code scanning library
    // For now, it's a placeholder
    setTimeout(function() {
        // Stop camera stream
        stream.getTracks().forEach(track => track.stop());
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('qrScannerModal')).hide();
        
        // Mock QR code result
        $(targetInput).val('SCANNED_QR_CODE_DATA');
    }, 5000);
}

// Print QR Codes
function printQRCodes(qrCodeIds) {
    const printWindow = window.open('', '_blank');
    let printContent = '<html><head><title>QR Kodları</title>';
    printContent += '<style>@media print { .qr-code { page-break-inside: avoid; margin: 1cm; text-align: center; } }</style>';
    printContent += '</head><body>';
    
    qrCodeIds.forEach(function(id) {
        const qrImage = document.querySelector(`[data-qr-id="${id}"] img`);
        const qrTitle = document.querySelector(`[data-qr-id="${id}"] .qr-title`).textContent;
        
        printContent += `<div class="qr-code">
            <h3>${qrTitle}</h3>
            <img src="${qrImage.src}" alt="QR Code" style="max-width: 200px;">
        </div>`;
    });
    
    printContent += '</body></html>';
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

// Warehouse Layout Visualization
function initWarehouseLayout(warehouseId) {
    $.get(`/api/v1/warehouses/${warehouseId}/layout/`, function(data) {
        renderWarehouseLayout(data);
    });
}

function renderWarehouseLayout(layoutData) {
    const container = document.getElementById('warehouse-layout');
    container.innerHTML = '';
    
    layoutData.corridors.forEach(function(corridor) {
        const corridorDiv = document.createElement('div');
        corridorDiv.className = 'corridor';
        corridorDiv.innerHTML = `<h6>Koridor ${corridor.number}</h6>`;
        
        corridor.cells.forEach(function(cell) {
            const cellDiv = document.createElement('div');
            cellDiv.className = `cell ${cell.status}`;
            cellDiv.textContent = cell.number;
            cellDiv.dataset.cellId = cell.id;
            cellDiv.dataset.cellInfo = JSON.stringify(cell);
            corridorDiv.appendChild(cellDiv);
        });
        
        container.appendChild(corridorDiv);
    });
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    let isValid = true;
    
    // Remove previous validation classes
    $(form).find('.is-invalid').removeClass('is-invalid');
    $(form).find('.invalid-feedback').remove();
    
    // Check required fields
    $(form).find('[required]').each(function() {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
            $(this).after('<div class="invalid-feedback">Bu alan gereklidir.</div>');
            isValid = false;
        }
    });
    
    return isValid;
}

// Export functionality
function exportData(format, url) {
    const exportUrl = `${url}?format=${format}`;
    window.location.href = exportUrl;
}