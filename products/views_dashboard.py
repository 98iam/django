from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import UserPreference

@login_required
def dashboard_settings(request):
    """View for dashboard customization settings"""
    # Get or create user preferences
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    # Get widget configurations
    widgets = preference.dashboard_widgets or preference.DEFAULT_DASHBOARD_WIDGETS

    # Define widget display names and descriptions
    widget_info = {
        'total_products': {
            'name': 'Total Products',
            'description': 'Shows the total number of products in your inventory.'
        },
        'total_categories': {
            'name': 'Total Categories',
            'description': 'Shows the total number of product categories.'
        },
        'low_stock_products': {
            'name': 'Low Stock Products',
            'description': 'Shows the number of products with stock below minimum level.'
        },
        'total_value': {
            'name': 'Total Inventory Value',
            'description': 'Shows the total value of your current inventory.'
        },
        'recent_products': {
            'name': 'Recent Products',
            'description': 'Shows a list of recently added products.'
        },
        'categories_with_counts': {
            'name': 'Categories Overview',
            'description': 'Shows categories with their product counts.'
        },
        'sales_trends_chart': {
            'name': 'Sales Trends Chart',
            'description': 'Shows a chart of your sales trends over time.'
        },
        'inventory_value_chart': {
            'name': 'Inventory Value Chart',
            'description': 'Shows a chart of your inventory value over time.'
        },
        'product_performance_chart': {
            'name': 'Product Performance Chart',
            'description': 'Shows a chart of your top performing products.'
        },
    }

    # Combine widget configurations with their info
    widget_data = []
    for widget_id, config in widgets.items():
        info = widget_info.get(widget_id, {'name': widget_id, 'description': ''})
        widget_data.append({
            'id': widget_id,
            'name': info['name'],
            'description': info['description'],
            'enabled': config.get('enabled', True),
            'order': config.get('order', 999)
        })

    # Sort widgets by their order
    widget_data.sort(key=lambda x: x['order'])

    context = {
        'widget_data': widget_data,
    }

    return render(request, 'products/dashboard_settings.html', context)

@login_required
@require_POST
def save_dashboard_settings(request):
    """Save dashboard widget settings"""
    try:
        data = json.loads(request.body)
        widgets_config = data.get('widgets', {})

        # Get or create user preferences
        preference, created = UserPreference.objects.get_or_create(user=request.user)

        # Update widget configurations
        current_widgets = preference.dashboard_widgets or preference.DEFAULT_DASHBOARD_WIDGETS

        for widget_id, config in widgets_config.items():
            if widget_id in current_widgets:
                current_widgets[widget_id]['enabled'] = config.get('enabled', True)
                current_widgets[widget_id]['order'] = config.get('order', 999)

        # Save updated configurations
        preference.dashboard_widgets = current_widgets
        preference.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def reset_dashboard_settings(request):
    """Reset dashboard widget settings to defaults (AJAX version)"""
    try:
        # Get user preferences
        preference, created = UserPreference.objects.get_or_create(user=request.user)

        # Reset to defaults with all chart widgets enabled
        default_widgets = {
            'total_products': {'enabled': True, 'order': 1},
            'total_categories': {'enabled': True, 'order': 2},
            'low_stock_products': {'enabled': True, 'order': 3},
            'total_value': {'enabled': True, 'order': 4},
            'recent_products': {'enabled': True, 'order': 5},
            'categories_with_counts': {'enabled': True, 'order': 6},
            'sales_trends_chart': {'enabled': True, 'order': 7},
            'inventory_value_chart': {'enabled': True, 'order': 8},
            'product_performance_chart': {'enabled': True, 'order': 9},
        }

        preference.dashboard_widgets = default_widgets
        preference.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def reset_dashboard(request):
    """Reset dashboard widget settings to defaults and redirect to dashboard"""
    try:
        # Get user preferences
        preference, created = UserPreference.objects.get_or_create(user=request.user)

        # Reset to defaults with all chart widgets enabled
        default_widgets = {
            'total_products': {'enabled': True, 'order': 1},
            'total_categories': {'enabled': True, 'order': 2},
            'low_stock_products': {'enabled': True, 'order': 3},
            'total_value': {'enabled': True, 'order': 4},
            'recent_products': {'enabled': True, 'order': 5},
            'categories_with_counts': {'enabled': True, 'order': 6},
            'sales_trends_chart': {'enabled': True, 'order': 7},
            'inventory_value_chart': {'enabled': True, 'order': 8},
            'product_performance_chart': {'enabled': True, 'order': 9},
        }

        # Force reset the dashboard widgets
        preference.dashboard_widgets = {}
        preference.save()

        # Set the default widgets again
        preference.dashboard_widgets = default_widgets
        preference.save()

        # Print the widgets to verify
        print("Reset dashboard widgets to:", preference.dashboard_widgets)
        print("Ordered widgets after reset:", [w[0] for w in preference.get_ordered_widgets()])

        messages.success(request, 'Dashboard settings have been reset to defaults with all chart widgets enabled.')
    except Exception as e:
        messages.error(request, f'Error resetting dashboard settings: {str(e)}')

    return redirect('dashboard')
