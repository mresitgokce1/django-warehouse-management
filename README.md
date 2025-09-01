# Django Warehouse Management System

Complete Django warehouse management system with QR codes, multi-brand support, and mobile-responsive design.

## Features

- **Multi-brand Operations**: Complete isolation between brands with role-based access control
- **User Management**: System Admin, Brand Admin, and Brand Personnel roles
- **QR Code Integration**: Automatic generation and mobile scanning support
- **Warehouse Management**: Hierarchical organization (Brand → Shop → Warehouse → Corridor → Cell)
- **Mobile Responsive**: Bootstrap 5 UI optimized for all devices
- **RESTful API**: Complete API for mobile app integration
- **Turkish Language Support**: Full localization for Turkish users
- **Production Ready**: Environment-based configuration and security best practices

## User Roles

### System Admin
- Full system access
- Can manage all brands and users
- System-wide configuration

### Brand Admin
- Full access to their brand operations
- Can manage brand users and permissions
- Brand-specific dashboard and reports

### Brand Personnel
- Limited access based on permissions set by Brand Admin
- Can perform daily warehouse operations
- Mobile-optimized interface

## Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/mresitgokce1/django-warehouse-management.git
cd django-warehouse-management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Load sample data (optional):
```bash
python manage.py loaddata sample_data.json
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
django_warehouse_management/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── django_warehouse_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/          # User management and authentication
│   ├── brands/            # Brand management and isolation
│   ├── products/          # Product catalog and inventory
│   ├── shops/             # Shop management
│   ├── warehouses/        # Warehouse, corridor, and cell management
│   └── qr_codes/          # QR code generation and scanning
├── templates/             # HTML templates
├── static/                # CSS, JS, and images
├── media/                 # User uploaded files
└── locale/                # Translation files
    └── tr/                # Turkish translations
```

## API Documentation

The system provides a complete RESTful API for mobile applications:

- `/api/auth/` - Authentication endpoints
- `/api/products/` - Product management
- `/api/warehouses/` - Warehouse operations
- `/api/qr-codes/` - QR code operations

## Features by App

### Accounts App
- Custom User model with role-based permissions
- Multi-brand user isolation
- Password reset and email verification
- Profile management

### Brands App
- Brand registration and management
- Logo and branding customization
- Brand-specific settings
- Multi-tenancy support

### Products App
- Complete product catalog
- Category management
- SKU and barcode generation
- Image gallery support
- Price and cost tracking
- Stock level monitoring

### Shops App
- Multiple shops per brand
- Location tracking with maps
- Shop manager assignment
- Contact information management

### Warehouses App
- Hierarchical storage system
- Corridor and cell organization
- Stock placement optimization
- Capacity management
- Location-based inventory

### QR Codes App
- Automatic QR generation
- Mobile scanning interface
- Product information display
- Location navigation QRs
- Printable labels

## Configuration

The system uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Security Features

- Role-based access control
- Brand data isolation
- CSRF protection
- Secure password requirements
- Session security
- XSS protection

## Mobile Features

- Responsive design for all screen sizes
- Touch-friendly interfaces
- QR code scanning with camera
- Offline capability (coming soon)
- Push notifications (coming soon)

## Deployment

The system is ready for production deployment with:

- WhiteNoise for static file serving
- Environment-based configuration
- Database optimization
- Error logging and monitoring
- Security best practices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub.
