from django import template
from django.contrib.auth.models import User
from auth_app.models import UserProfile

register = template.Library()

@register.filter
def currency(value):
    """
    Format a value as currency using the Indian Rupee symbol.
    This is a temporary solution to always show INR regardless of user preference.
    """
    try:
        # Always use INR symbol
        return f"₹{float(value):.2f}"
    except (ValueError, TypeError):
        return value

@register.simple_tag(takes_context=True)
def user_currency_symbol(context):
    """
    Return the currency symbol for the current user.
    """
    request = context.get('request')
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        try:
            if hasattr(request.user, 'profile'):
                currency_code = request.user.profile.currency
                # For now, always return INR symbol
                return "₹"
        except Exception:
            pass
    return "₹"  # Default to INR
