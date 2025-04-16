from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

def product_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/products/user_<id>/<filename>
    return f'products/user_{instance.user.id}/{filename}'

class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    barcode = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Purchase cost per unit")
    quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0, help_text="Minimum stock level before reorder")
    maximum_stock = models.IntegerField(default=0, help_text="Maximum stock level")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Storage location")
    supplier = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, help_text="Product image")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.minimum_stock > self.maximum_stock:
            raise ValidationError("Minimum stock cannot be greater than maximum stock")
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")

    @property
    def stock_status(self):
        if self.quantity <= self.minimum_stock:
            return "Low Stock"
        elif self.quantity >= self.maximum_stock:
            return "Overstocked"
        return "Normal"

    @property
    def profit_margin(self):
        try:
            if self.cost and self.cost > 0:
                return ((self.price - self.cost) / self.cost) * 100
            return 0
        except (TypeError, ZeroDivisionError):
            return 0

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    sale_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale #{self.invoice_number}"

    def save(self, *args, **kwargs):
        # Calculate total amount from sale items if not set
        if not self.total_amount:
            self.total_amount = sum(item.subtotal for item in self.items.all())
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of sale
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price

class InventorySnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_snapshots')
    date = models.DateField(default=timezone.now)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_products = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Inventory Snapshot {self.date}"

class SavedReport(models.Model):
    REPORT_TYPES = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('product', 'Product Performance'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    configuration = models.JSONField(default=dict)  # Stores report configuration as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    # Default dashboard widgets and their order
    DEFAULT_DASHBOARD_WIDGETS = {
        'total_products': {'enabled': True, 'order': 1},
        'total_categories': {'enabled': True, 'order': 2},
        'low_stock_products': {'enabled': True, 'order': 3},
        'total_value': {'enabled': True, 'order': 4},
        'sales_trends_chart': {'enabled': True, 'order': 5},
        'inventory_value_chart': {'enabled': True, 'order': 6},
        'product_performance_chart': {'enabled': True, 'order': 7},
        'recent_products': {'enabled': True, 'order': 8},
        'categories_with_counts': {'enabled': True, 'order': 9},
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    dashboard_widgets = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    def save(self, *args, **kwargs):
        # Initialize dashboard_widgets with defaults if empty
        if not self.dashboard_widgets:
            self.dashboard_widgets = self.DEFAULT_DASHBOARD_WIDGETS
        super().save(*args, **kwargs)

    def get_widget_config(self, widget_name):
        """Get configuration for a specific widget"""
        if not self.dashboard_widgets:
            return self.DEFAULT_DASHBOARD_WIDGETS.get(widget_name)
        return self.dashboard_widgets.get(widget_name, self.DEFAULT_DASHBOARD_WIDGETS.get(widget_name))

    def is_widget_enabled(self, widget_name):
        """Check if a widget is enabled"""
        widget_config = self.get_widget_config(widget_name)
        if widget_config:
            return widget_config.get('enabled', True)
        return True  # Default to enabled if config not found

    def get_ordered_widgets(self):
        """Get widgets ordered by their order value"""
        if not self.dashboard_widgets:
            widgets = self.DEFAULT_DASHBOARD_WIDGETS
        else:
            widgets = self.dashboard_widgets

        # Filter enabled widgets and sort by order
        enabled_widgets = {k: v for k, v in widgets.items() if v.get('enabled', True)}
        return sorted(enabled_widgets.items(), key=lambda x: x[1].get('order', 999))
