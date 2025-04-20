from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import json
from .models import Product, Category, UserPreference, Sale, SaleItem, InventorySnapshot
from .forms import ProductForm, CategoryForm
from .export import (
    export_products_csv, export_products_excel, export_products_pdf,
    export_categories_csv, export_categories_excel, export_categories_pdf
)
from .views_analytics import generate_demo_sales_data, generate_demo_inventory_data, generate_demo_performance_data, DecimalEncoder

# Test view to check if server is running
def test_view(request):
    return HttpResponse("Server is running!")

# Landing page view
def landing_page(request):
    # Always show the landing page, even for authenticated users
    return render(request, 'landing_page.html')

# Test view for Chart.js
def test_chart(request):
    return render(request, 'products/test_chart.html')

@login_required
def dashboard(request):
    # Get user preferences for dashboard widgets
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    # Prepare data for all widgets
    widget_data = {}

    # Only calculate data for enabled widgets
    if preference.is_widget_enabled('total_products'):
        widget_data['total_products'] = Product.objects.filter(user=request.user).count()

    if preference.is_widget_enabled('total_categories'):
        widget_data['total_categories'] = Category.objects.filter(user=request.user).count()

    if preference.is_widget_enabled('low_stock_products'):
        widget_data['low_stock_products'] = Product.objects.filter(
            user=request.user, quantity__lte=F('minimum_stock')).count()

    if preference.is_widget_enabled('total_value'):
        widget_data['total_value'] = Product.objects.filter(user=request.user).aggregate(
            total=Sum(F('quantity') * F('cost')))['total'] or 0

    if preference.is_widget_enabled('recent_products'):
        widget_data['recent_products'] = Product.objects.filter(
            user=request.user).order_by('-created_at')[:5]

    if preference.is_widget_enabled('categories_with_counts'):
        widget_data['categories_with_counts'] = Category.objects.filter(user=request.user).annotate(
            product_count=Count('products')).order_by('-product_count')[:5]

    # Add data for sales trends chart
    if preference.is_widget_enabled('sales_trends_chart'):

        # Get sales data for the last 30 days
        days = 30
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        # Get sales data
        sales = Sale.objects.filter(
            user=request.user,
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).order_by('sale_date')

        # For demo purposes, if no sales data exists, create some random data
        if not sales.exists():
            sales_data = generate_demo_sales_data(request.user, days)
        else:
            # Group sales by date
            sales_by_date = {}
            for sale in sales:
                date_str = sale.sale_date.date().strftime('%Y-%m-%d')
                if date_str in sales_by_date:
                    sales_by_date[date_str] += sale.total_amount
                else:
                    sales_by_date[date_str] = sale.total_amount

            # Create a list of dates and corresponding sales amounts
            dates = []
            amounts = []
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                dates.append(date_str)
                amounts.append(float(sales_by_date.get(date_str, 0)))
                current_date += timedelta(days=1)

            sales_data = {
                'dates': dates,
                'amounts': amounts
            }

        try:
            # Ensure the data is properly formatted
            for i, amount in enumerate(sales_data['amounts']):
                sales_data['amounts'][i] = float(amount)

            widget_data['sales_trends_chart'] = json.dumps(sales_data, cls=DecimalEncoder)
            print("Sales trends chart data:", widget_data['sales_trends_chart'][:100], "...")
        except Exception as e:
            print(f"Error serializing sales data: {e}")
            widget_data['sales_trends_chart'] = 'null'

    # Add data for inventory value chart
    if preference.is_widget_enabled('inventory_value_chart'):

        # Get inventory data for the last 30 days
        days = 30
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        # Get inventory snapshots
        snapshots = InventorySnapshot.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        # For demo purposes, if no snapshot data exists, create some random data
        if not snapshots.exists():
            inventory_data = generate_demo_inventory_data(request.user, days)
        else:
            # Create a dictionary of dates and values
            inventory_by_date = {snapshot.date.strftime('%Y-%m-%d'): float(snapshot.total_value) for snapshot in snapshots}

            # Create a list of dates and corresponding inventory values
            dates = []
            values = []
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                dates.append(date_str)
                values.append(inventory_by_date.get(date_str, 0))
                current_date += timedelta(days=1)

            inventory_data = {
                'dates': dates,
                'values': values
            }

        try:
            # Ensure the data is properly formatted
            for i, value in enumerate(inventory_data['values']):
                inventory_data['values'][i] = float(value)

            widget_data['inventory_value_chart'] = json.dumps(inventory_data, cls=DecimalEncoder)
            print("Inventory value chart data:", widget_data['inventory_value_chart'][:100], "...")
        except Exception as e:
            print(f"Error serializing inventory data: {e}")
            widget_data['inventory_value_chart'] = 'null'

    # Add data for product performance chart
    if preference.is_widget_enabled('product_performance_chart'):

        # Get products
        products = Product.objects.filter(user=request.user)

        # For demo purposes, if no sales data exists, create some random data
        if not SaleItem.objects.filter(product__user=request.user).exists():
            performance_data = generate_demo_performance_data(products)
        else:
            # Get sales data for each product
            product_sales = {}
            for product in products:
                sales_count = SaleItem.objects.filter(product=product).aggregate(
                    total_quantity=Sum('quantity'),
                    total_revenue=Sum(F('quantity') * F('price'))
                )
                product_sales[product.id] = {
                    'name': product.name,
                    'quantity': sales_count['total_quantity'] or 0,
                    'revenue': float(sales_count['total_revenue'] or 0),
                    'profit_margin': product.profit_margin
                }

            # Sort products by revenue
            sorted_products = sorted(product_sales.values(), key=lambda x: x['revenue'], reverse=True)[:10]

            performance_data = {
                'products': [p['name'] for p in sorted_products],
                'quantities': [p['quantity'] for p in sorted_products],
                'revenues': [p['revenue'] for p in sorted_products],
                'margins': [p['profit_margin'] for p in sorted_products]
            }

        try:
            # Ensure the data is properly formatted
            for i, revenue in enumerate(performance_data['revenues']):
                performance_data['revenues'][i] = float(revenue)
            for i, margin in enumerate(performance_data['margins']):
                performance_data['margins'][i] = float(margin)

            widget_data['product_performance_chart'] = json.dumps(performance_data, cls=DecimalEncoder)
            print("Product performance chart data:", widget_data['product_performance_chart'][:100], "...")
        except Exception as e:
            print(f"Error serializing performance data: {e}")
            widget_data['product_performance_chart'] = 'null'

    # Get ordered widgets for display
    ordered_widgets = preference.get_ordered_widgets()

    # Debug: Print widget data and ordered widgets
    print("Widget data keys:", widget_data.keys())
    print("Ordered widgets:", [w[0] for w in ordered_widgets])

    # Force-enable chart widgets for debugging
    if 'sales_trends_chart' not in widget_data and preference.is_widget_enabled('sales_trends_chart'):
        print("Sales trends chart is enabled but data is missing")
    if 'inventory_value_chart' not in widget_data and preference.is_widget_enabled('inventory_value_chart'):
        print("Inventory value chart is enabled but data is missing")
    if 'product_performance_chart' not in widget_data and preference.is_widget_enabled('product_performance_chart'):
        print("Product performance chart is enabled but data is missing")

    context = {
        'widget_data': widget_data,
        'ordered_widgets': ordered_widgets,
        'show_customize_button': True,
    }
    return render(request, 'products/dashboard.html', context)

@login_required
def product_list(request):
    # Filter products by the current user
    products = Product.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Status filter
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)

    # Low stock filter
    if request.GET.get('low_stock'):
        products = products.filter(quantity__lte=F('minimum_stock'))

    products = products.select_related('category').order_by('name')

    # Handle export requests
    export_format = request.GET.get('export')
    if export_format:
        if export_format == 'csv':
            return export_products_csv(products)
        elif export_format == 'excel':
            return export_products_excel(products)
        elif export_format == 'pdf':
            return export_products_pdf(products)

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    # Ensure the product belongs to the current user
    product = get_object_or_404(Product, pk=pk, user=request.user)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.user = request.user
                product.save()
                messages.success(request, f'Product "{product.name}" created successfully.')
                return redirect('product_list')
            except Exception as e:
                messages.error(request, f'Error saving product: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            # Print form errors for debugging
            print("Form errors:", form.errors)
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Create Product'
    })

@login_required
def product_edit(request, pk):
    # Ensure the product belongs to the current user
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def product_delete(request, pk):
    # Ensure the product belongs to the current user
    product = get_object_or_404(Product, pk=pk, user=request.user)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    # Filter categories by the current user
    categories = Category.objects.filter(user=request.user).annotate(
        product_count=Count('products')).order_by('name')

    # Handle export requests
    export_format = request.GET.get('export')
    if export_format:
        if export_format == 'csv':
            return export_categories_csv(categories)
        elif export_format == 'excel':
            return export_categories_excel(categories)
        elif export_format == 'pdf':
            return export_categories_pdf(categories)

    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                messages.success(request, f'Category "{category.name}" created successfully.')
                return redirect('category_list')
            except Exception as e:
                messages.error(request, f'Error saving category: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()

    return render(request, 'products/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })

@login_required
def category_delete(request, pk):
    # Ensure the category belongs to the current user
    category = get_object_or_404(Category, pk=pk, user=request.user)

    # Check if the category has associated products
    product_count = category.products.count()

    if request.method == 'POST':
        category_name = category.name

        # Check if force delete is requested
        force_delete = request.POST.get('force_delete') == 'yes'

        if product_count > 0 and not force_delete:
            messages.error(request, f'Cannot delete category "{category_name}" because it has {product_count} associated products. Please delete the products first or use force delete.')
            return redirect('category_delete', pk=pk)

        try:
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully.')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
            return redirect('category_list')

    return render(request, 'products/category_confirm_delete.html', {
        'category': category,
        'product_count': product_count
    })
# Create your views here.
