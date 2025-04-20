from django.urls import path
from . import views
from . import views_settings
from . import views_debug

urlpatterns = [
    # Authentication views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'), # OTP verification for registration
    path('verify-login-otp/', views.verify_login_otp_view, name='verify_login_otp'), # OTP verification for login
    path('resend-otp/', views.resend_otp_view, name='resend_otp'), # Resend OTP
    path('setup-otp/', views.setup_otp_view, name='setup_otp'), # Setup OTP instructions

    # Settings views
    path('settings/profile/', views_settings.settings_profile, name='settings_profile'),
    path('settings/appearance/', views_settings.settings_appearance, name='settings_appearance'),
    path('settings/notifications/', views_settings.settings_notifications, name='settings_notifications'),
    path('settings/security/', views_settings.settings_security, name='settings_security'),
    path('settings/save-appearance/', views_settings.save_appearance_settings, name='save_appearance_settings'),
    path('settings/send-test-email/', views_settings.send_test_email, name='send_test_email'),

    # Debug views
    path('debug/profile/', views_debug.debug_user_profile, name='debug_user_profile'),
]
