from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os

class SupabaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    supabase_uid = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.user.username

def profile_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'profile_images/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('es', _('Spanish')),
        ('fr', _('French')),
        ('de', _('German')),
    ]

    TIMEZONE_CHOICES = [
        ('UTC', 'UTC'),
        ('US/Eastern', 'US/Eastern'),
        ('US/Central', 'US/Central'),
        ('US/Pacific', 'US/Pacific'),
        ('Europe/London', 'Europe/London'),
        ('Europe/Paris', 'Europe/Paris'),
        ('Asia/Tokyo', 'Asia/Tokyo'),
    ]

    DATE_FORMAT_CHOICES = [
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
    ]

    CURRENCY_CHOICES = [
        ('USD', _('US Dollar ($)')),
        ('INR', _('Indian Rupee (₹)')),
        ('EUR', _('Euro (€)')),
        ('GBP', _('British Pound (£)')),
        ('JPY', _('Japanese Yen (¥)')),
        ('CAD', _('Canadian Dollar (C$)')),
        ('AUD', _('Australian Dollar (A$)')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    date_format = models.CharField(max_length=20, choices=DATE_FORMAT_CHOICES, default='MM/DD/YYYY')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    low_stock_alerts = models.BooleanField(default=True)
    order_updates = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def delete(self, *args, **kwargs):
        # Delete the profile image when the profile is deleted
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
        super().delete(*args, **kwargs)