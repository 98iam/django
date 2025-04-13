from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

# Import mock data for fallback
from .mock_data import get_mock_inventory_summary, get_mock_product_info, get_mock_sales_analytics

# Import utility functions
from .utils import format_currency, get_currency_symbol

# Import models - with error handling for testing
try:
    from products.models import Product, Category, Sale
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    logging.warning("Product models not available. Using mock data for testing.")

# Get logger
logger = logging.getLogger(__name__)

class InventoryContext:
    """
    Class to retrieve and format inventory data for AI context
    """

    @staticmethod
    def get_product_info(query=None, limit=10, user=None):
        """
        Get information about products matching the query

        Args:
            query: Search term for products
            limit: Maximum number of products to return

        Returns:
            Formatted string with product information
        """
        if not MODELS_AVAILABLE:
            logger.info("Using mock product data")
            # Get currency symbol if user has a preference
            currency_symbol = '$'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_symbol = get_currency_symbol(user.profile.currency)
                except Exception as e:
                    logger.error(f"Error getting user currency symbol: {str(e)}")

            return get_mock_product_info(currency_symbol)

        try:
            # Filter products by user if provided
            if user:
                logger.info(f"Filtering products for user: {user.username}")
                products = Product.objects.filter(user=user)
                total_count = products.count()
            else:
                logger.info("No user provided, showing all products")
                products = Product.objects.all()
                total_count = products.count()

            logger.info(f"Total products for this user: {total_count}")

            if total_count == 0:
                return "There are no products in your inventory."

            # Filter by query if provided
            if query:
                products = products.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(sku__icontains=query)
                )

            # Order by creation date to identify oldest/newest products
            products = products.order_by('created_at')
            product_list = list(products[:limit])  # Force evaluation of the queryset

            if not product_list:
                if query:
                    return f"No products found matching '{query}'."
                else:
                    return "No products found in the inventory."

            # Get user's currency preference if available
            currency_code = 'USD'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_code = user.profile.currency
                except Exception as e:
                    logger.error(f"Error getting user currency: {str(e)}")

            # Format product information with more details
            result = "Product Information:\n"
            for product in product_list:
                # Calculate product value and profit
                product_value = product.price * product.quantity
                profit_per_unit = product.price - product.cost
                total_profit_potential = profit_per_unit * product.quantity

                result += f"- {product.name} (SKU: {product.sku})\n"
                result += f"  Description: {product.description or 'No description available'}\n"
                result += f"  Category: {product.category.name if product.category else 'Uncategorized'}\n"
                result += f"  Price: {format_currency(product.price, currency_code)}\n"
                result += f"  Cost: {format_currency(product.cost, currency_code)}\n"
                result += f"  Profit Margin: {product.profit_margin:.2f}%\n"
                result += f"  In Stock: {product.quantity}\n"
                result += f"  Total Value: {format_currency(product_value, currency_code)}\n"
                result += f"  Potential Profit: {format_currency(total_profit_potential, currency_code)}\n"
                result += f"  Minimum Stock: {product.minimum_stock}\n"
                result += f"  Maximum Stock: {product.maximum_stock}\n"
                result += f"  Stock Status: {product.stock_status}\n"
                result += f"  Location: {product.location or 'Not specified'}\n"
                result += f"  Supplier: {product.supplier or 'Not specified'}\n"
                result += f"  Created: {product.created_at.strftime('%Y-%m-%d')}\n"
                result += f"  Last Updated: {product.updated_at.strftime('%Y-%m-%d')}\n"
                result += f"  Status: {product.status}\n"
                result += "\n"

            # Add information about oldest and newest products
            if len(product_list) > 0:
                oldest_product = products.first()
                newest_product = products.order_by('-created_at').first()

                result += "Product Age Information:\n"
                result += f"Oldest Product: {oldest_product.name} (Created: {oldest_product.created_at.strftime('%Y-%m-%d')})\n"
                result += f"Newest Product: {newest_product.name} (Created: {newest_product.created_at.strftime('%Y-%m-%d')})\n\n"

            return result

        except Exception as e:
            logger.error(f"Error retrieving product info: {str(e)}")
            logger.info("Falling back to mock product data")
            return get_mock_product_info()

    @staticmethod
    def get_inventory_summary(user=None):
        """
        Get a summary of the current inventory

        Returns:
            Formatted string with inventory summary
        """
        if not MODELS_AVAILABLE:
            logger.info("Using mock inventory summary")
            # Get currency symbol if user has a preference
            currency_symbol = '$'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_symbol = get_currency_symbol(user.profile.currency)
                except Exception as e:
                    logger.error(f"Error getting user currency symbol: {str(e)}")

            return get_mock_inventory_summary(currency_symbol)

        try:
            # Filter by user if provided
            if user:
                logger.info(f"Filtering inventory summary for user: {user.username}")
                products = Product.objects.filter(user=user)
            else:
                logger.info("No user provided, showing all products in summary")
                products = Product.objects.all()

            # Get basic counts
            total_products = products.count()
            logger.info(f"Total products for summary: {total_products}")

            if total_products == 0:
                return "There are no products in your inventory."

            # Get category counts for this user's products
            if user:
                # Get categories that have products owned by this user
                category_ids = products.values_list('category', flat=True).distinct()
                total_categories = Category.objects.filter(id__in=category_ids).count()
            else:
                total_categories = Category.objects.count()

            # Calculate inventory metrics
            total_stock = products.aggregate(total=Sum('quantity'))['total'] or 0
            low_stock = products.filter(quantity__lte=10).count()
            out_of_stock = products.filter(quantity=0).count()

            # Calculate financial metrics
            total_inventory_value = sum(product.price * product.quantity for product in products)
            total_inventory_cost = sum(product.cost * product.quantity for product in products)
            total_potential_profit = total_inventory_value - total_inventory_cost
            avg_profit_margin = sum(product.profit_margin for product in products) / total_products if total_products > 0 else 0

            # Get time-based information
            oldest_product = products.order_by('created_at').first() if total_products > 0 else None
            newest_product = products.order_by('-created_at').first() if total_products > 0 else None

            # Get stock status counts
            normal_stock = products.filter(quantity__gt=10).count()
            overstocked = products.filter(quantity__gte=F('maximum_stock'), maximum_stock__gt=0).count()

            # Get some sample products to show
            sample_products = list(products[:5])

            # Build the summary with more comprehensive information
            result = "Inventory Summary:\n"
            result += f"Total Products: {total_products}\n"
            result += f"Total Categories: {total_categories}\n"
            result += f"Total Items in Stock: {total_stock}\n"

            # Stock status section
            result += "\nStock Status:\n"
            result += f"Normal Stock Items: {normal_stock}\n"
            result += f"Low Stock Items (<=10): {low_stock}\n"
            result += f"Out of Stock Items: {out_of_stock}\n"
            result += f"Overstocked Items: {overstocked}\n"

            # Get user's currency preference if available
            currency_code = 'USD'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_code = user.profile.currency
                except Exception as e:
                    logger.error(f"Error getting user currency: {str(e)}")

            # Financial metrics section
            result += "\nFinancial Metrics:\n"
            result += f"Total Inventory Value: {format_currency(total_inventory_value, currency_code)}\n"
            result += f"Total Inventory Cost: {format_currency(total_inventory_cost, currency_code)}\n"
            result += f"Total Potential Profit: {format_currency(total_potential_profit, currency_code)}\n"
            result += f"Average Profit Margin: {avg_profit_margin:.2f}%\n"

            # Time-based information
            result += "\nInventory Timeline:\n"
            if oldest_product:
                result += f"Oldest Product: {oldest_product.name} (Added: {oldest_product.created_at.strftime('%Y-%m-%d')})\n"
            if newest_product:
                result += f"Newest Product: {newest_product.name} (Added: {newest_product.created_at.strftime('%Y-%m-%d')})\n"
            result += "\n"

            # Add sample products with more details
            if sample_products:
                result += "Sample Products:\n"
                for product in sample_products:
                    product_value = product.price * product.quantity
                    result += f"- {product.name}: {product.quantity} in stock, {format_currency(product.price, currency_code)} each, total value: {format_currency(product_value, currency_code)}\n"
                result += "\n"

            # Get top categories by product count if any exist
            if total_categories > 0:
                try:
                    if user:
                        # Get categories with product counts for this user only
                        category_ids = products.values_list('category', flat=True).distinct()
                        top_categories = Category.objects.filter(id__in=category_ids).annotate(
                            product_count=Count('products', filter=Q(products__user=user))
                        ).order_by('-product_count')[:5]
                    else:
                        # Get categories for all products
                        top_categories = Category.objects.annotate(
                            product_count=Count('products')
                        ).order_by('-product_count')[:5]

                    category_list = list(top_categories)  # Force evaluation

                    if category_list:
                        result += "Categories:\n"
                        for category in category_list:
                            # Calculate category value
                            category_products = products.filter(category=category)
                            category_value = sum(p.price * p.quantity for p in category_products)
                            category_items = sum(p.quantity for p in category_products)

                            result += f"- {category.name}: {category.product_count} products, {category_items} items, value: {format_currency(category_value, currency_code)}\n"
                except Exception as category_error:
                    logger.error(f"Error getting categories: {str(category_error)}")
                    result += "\nNote: Unable to retrieve category information.\n"

            return result

        except Exception as e:
            logger.error(f"Error retrieving inventory summary: {str(e)}")
            logger.info("Falling back to mock inventory summary")
            return get_mock_inventory_summary()

    @staticmethod
    def get_sales_analytics(user=None):
        """
        Get sales analytics data

        Returns:
            Formatted string with sales analytics
        """
        if not MODELS_AVAILABLE:
            logger.info("Using mock sales analytics")
            # Get currency symbol if user has a preference
            currency_symbol = '$'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_symbol = get_currency_symbol(user.profile.currency)
                except Exception as e:
                    logger.error(f"Error getting user currency symbol: {str(e)}")

            return get_mock_sales_analytics(currency_symbol)

        try:
            # Filter sales by user if provided
            if user:
                logger.info(f"Filtering sales for user: {user.username}")
                sales = Sale.objects.filter(user=user)
            else:
                logger.info("No user provided, showing all sales")
                sales = Sale.objects.all()

            # Check if there are any sales
            total_sales = sales.count()
            logger.info(f"Total sales for analytics: {total_sales}")

            if total_sales == 0:
                return "There are no sales records for your account."

            # Get total revenue
            total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0

            # Get time-based sales data
            thirty_days_ago = timezone.now() - timedelta(days=30)
            seven_days_ago = timezone.now() - timedelta(days=7)
            today = timezone.now().date()

            # Last 30 days
            recent_sales = sales.filter(sale_date__gte=thirty_days_ago)
            recent_count = recent_sales.count()
            recent_revenue = recent_sales.aggregate(total=Sum('total_amount'))['total'] or 0

            # Last 7 days
            weekly_sales = sales.filter(sale_date__gte=seven_days_ago)
            weekly_count = weekly_sales.count()
            weekly_revenue = weekly_sales.aggregate(total=Sum('total_amount'))['total'] or 0

            # Today
            today_sales = sales.filter(sale_date__date=today)
            today_count = today_sales.count()
            today_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0

            # Get oldest and newest sales
            oldest_sale = sales.order_by('sale_date').first()
            newest_sale = sales.order_by('-sale_date').first()

            # Calculate average sale value
            avg_sale_value = total_revenue / total_sales if total_sales > 0 else 0

            # Get payment method breakdown
            payment_methods = {}
            for method_choice in Sale.PAYMENT_METHODS:
                method_code = method_choice[0]
                method_name = method_choice[1]
                count = sales.filter(payment_method=method_code).count()
                if count > 0:
                    payment_methods[method_name] = count

            # Get user's currency preference if available
            currency_code = 'USD'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_code = user.profile.currency
                except Exception as e:
                    logger.error(f"Error getting user currency: {str(e)}")

            # Build the result with comprehensive information
            result = "Sales Analytics:\n"
            result += f"Total Sales: {total_sales}\n"
            result += f"Total Revenue: {format_currency(total_revenue, currency_code)}\n"
            result += f"Average Sale Value: {format_currency(avg_sale_value, currency_code)}\n\n"

            # Time-based analytics
            result += "Time-Based Analytics:\n"
            result += f"Today: {today_count} sales, {format_currency(today_revenue, currency_code)} revenue\n"
            result += f"Last 7 Days: {weekly_count} sales, {format_currency(weekly_revenue, currency_code)} revenue\n"
            result += f"Last 30 Days: {recent_count} sales, {format_currency(recent_revenue, currency_code)} revenue\n"

            if oldest_sale:
                result += f"First Sale: {oldest_sale.sale_date.strftime('%Y-%m-%d')}\n"
            if newest_sale:
                result += f"Latest Sale: {newest_sale.sale_date.strftime('%Y-%m-%d')}\n"
            result += "\n"

            # Payment method breakdown
            if payment_methods:
                result += "Payment Methods:\n"
                for method, count in payment_methods.items():
                    percentage = (count / total_sales) * 100
                    result += f"- {method}: {count} sales ({percentage:.1f}%)\n"
                result += "\n"

            # Try to get top selling products with more details
            try:
                if user:
                    # Get top selling products for this user only
                    top_products = Product.objects.filter(user=user).annotate(
                        sale_count=Count('sale_items'),
                        revenue=Sum(F('sale_items__price') * F('sale_items__quantity'))
                    ).order_by('-sale_count')[:5]
                else:
                    # Get top selling products across all users
                    top_products = Product.objects.annotate(
                        sale_count=Count('sale_items'),
                        revenue=Sum(F('sale_items__price') * F('sale_items__quantity'))
                    ).order_by('-sale_count')[:5]

                product_list = list(top_products)  # Force evaluation

                if product_list:
                    result += "Top Selling Products:\n"
                    for product in product_list:
                        revenue = product.revenue or 0
                        result += f"- {product.name}: {product.sale_count} sales, {format_currency(revenue, currency_code)} revenue\n"

                    # Also show products by revenue
                    result += "\nTop Products by Revenue:\n"
                    for product in sorted(product_list, key=lambda p: p.revenue or 0, reverse=True)[:5]:
                        revenue = product.revenue or 0
                        result += f"- {product.name}: {format_currency(revenue, currency_code)} revenue, {product.sale_count} sales\n"
            except Exception as product_error:
                logger.error(f"Error getting top products: {str(product_error)}")
                result += "\nNote: Unable to retrieve top selling products.\n"

            # Try to get category sales data
            try:
                if user:
                    # Get categories with sales data for this user only
                    category_sales = Category.objects.filter(products__user=user).annotate(
                        sale_count=Count('products__sale_items', distinct=True),
                        revenue=Sum(F('products__sale_items__price') * F('products__sale_items__quantity'))
                    ).order_by('-revenue')[:5]
                else:
                    # Get categories for all sales
                    category_sales = Category.objects.annotate(
                        sale_count=Count('products__sale_items', distinct=True),
                        revenue=Sum(F('products__sale_items__price') * F('products__sale_items__quantity'))
                    ).order_by('-revenue')[:5]

                category_list = list(category_sales)  # Force evaluation

                if category_list:
                    result += "\nTop Categories by Revenue:\n"
                    for category in category_list:
                        revenue = category.revenue or 0
                        if revenue > 0:  # Only show categories with sales
                            result += f"- {category.name}: {format_currency(revenue, currency_code)} revenue, {category.sale_count} sales\n"
            except Exception as category_error:
                logger.error(f"Error getting category sales: {str(category_error)}")
                # Don't add error message to result if this fails

            return result

        except Exception as e:
            logger.error(f"Error retrieving sales analytics: {str(e)}")
            logger.info("Falling back to mock sales analytics")
            return get_mock_sales_analytics()

    @staticmethod
    def get_relevant_context(user_message, user=None):
        """
        Get relevant context based on the user's message

        Args:
            user_message: The user's message
            user: The user making the request (for filtering data)

        Returns:
            Formatted string with relevant context
        """
        if not MODELS_AVAILABLE:
            logger.warning("Models not available when getting context, using mock data")
            # Get currency symbol if user has a preference
            currency_symbol = '$'  # Default
            if user and hasattr(user, 'profile'):
                try:
                    currency_symbol = get_currency_symbol(user.profile.currency)
                except Exception as e:
                    logger.error(f"Error getting user currency symbol: {str(e)}")

            # Use mock data instead of returning an error
            context = get_mock_inventory_summary(currency_symbol)
            context += "\n\n" + get_mock_product_info(currency_symbol)
            context += "\n\n" + get_mock_sales_analytics(currency_symbol)
            return context

        user_message = user_message.lower()
        logger.info(f"Getting context for message: {user_message}")

        # Initialize context with basic inventory summary
        # Always include this for any inventory-related question
        context = InventoryContext.get_inventory_summary(user=user)

        # Check for specific product queries
        product_query = None
        product_keywords = ["product", "item", "stock", "price", "sku", "quantity", "description",
                           "profit margin", "value", "cost", "supplier", "location"]

        # Check for specific product name in the query
        if any(keyword in user_message for keyword in product_keywords):
            # Try to extract product name from query
            # First get all product names from the database
            if user:
                all_products = Product.objects.filter(user=user)
            else:
                all_products = Product.objects.all()

            product_names = [p.name.lower() for p in all_products]

            # Check if any product name is mentioned in the query
            for name in product_names:
                if name in user_message:
                    product_query = name
                    logger.info(f"Found specific product in query: {product_query}")
                    break

            # Get product info - if specific product found, use it as query
            product_info = InventoryContext.get_product_info(query=product_query, user=user)
            context += "\n\n" + product_info
            logger.info(f"Added product info: {len(product_info)} chars")

        # Check for time-related queries
        time_keywords = ["oldest", "newest", "recent", "latest", "first", "last", "date", "time",
                        "created", "updated", "when", "history", "timeline"]

        if any(keyword in user_message for keyword in time_keywords):
            # For time queries, make sure we have the oldest/newest product info
            if user:
                products = Product.objects.filter(user=user).order_by('created_at')
            else:
                products = Product.objects.all().order_by('created_at')

            if products.exists():
                oldest_product = products.first()
                newest_product = products.order_by('-created_at').first()

                time_info = "\nProduct Timeline Information:\n"
                time_info += f"Oldest Product: {oldest_product.name} (Created: {oldest_product.created_at.strftime('%Y-%m-%d')})\n"
                time_info += f"Newest Product: {newest_product.name} (Created: {newest_product.created_at.strftime('%Y-%m-%d')})\n"

                # Add more detailed time information for the oldest and newest products
                time_info += "\nOldest Product Details:\n"
                time_info += f"Name: {oldest_product.name}\n"
                time_info += f"SKU: {oldest_product.sku}\n"
                time_info += f"Category: {oldest_product.category.name if oldest_product.category else 'Uncategorized'}\n"
                time_info += f"Created: {oldest_product.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                time_info += f"Last Updated: {oldest_product.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

                time_info += "\nNewest Product Details:\n"
                time_info += f"Name: {newest_product.name}\n"
                time_info += f"SKU: {newest_product.sku}\n"
                time_info += f"Category: {newest_product.category.name if newest_product.category else 'Uncategorized'}\n"
                time_info += f"Created: {newest_product.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                time_info += f"Last Updated: {newest_product.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

                context += "\n" + time_info
                logger.info(f"Added timeline information: {len(time_info)} chars")

        # Check for value and financial queries
        value_keywords = ["value", "worth", "cost", "profit", "margin", "financial", "money",
                         "revenue", "price", "expensive", "cheap", "total value", "inventory value"]

        if any(keyword in user_message for keyword in value_keywords):
            # Calculate total inventory value
            if user:
                products = Product.objects.filter(user=user)
            else:
                products = Product.objects.all()

            if products.exists():
                total_value = sum(p.price * p.quantity for p in products)
                total_cost = sum(p.cost * p.quantity for p in products)
                total_profit = total_value - total_cost

                # Get user's currency preference if available
                currency_code = 'USD'  # Default
                if user and hasattr(user, 'profile'):
                    try:
                        currency_code = user.profile.currency
                    except Exception as e:
                        logger.error(f"Error getting user currency: {str(e)}")

                value_info = "\nInventory Value Information:\n"
                value_info += f"Total Inventory Value: {format_currency(total_value, currency_code)}\n"
                value_info += f"Total Inventory Cost: {format_currency(total_cost, currency_code)}\n"
                value_info += f"Total Potential Profit: {format_currency(total_profit, currency_code)}\n"

                # Get most valuable products
                valuable_products = sorted(products, key=lambda p: p.price * p.quantity, reverse=True)[:5]

                value_info += "\nMost Valuable Products (by total value):\n"
                for product in valuable_products:
                    product_value = product.price * product.quantity
                    value_info += f"- {product.name}: {format_currency(product_value, currency_code)} ({format_currency(product.price, currency_code)} × {product.quantity})\n"

                # Get highest margin products
                margin_products = sorted(products, key=lambda p: p.profit_margin, reverse=True)[:5]

                value_info += "\nHighest Margin Products:\n"
                for product in margin_products:
                    value_info += f"- {product.name}: {product.profit_margin:.2f}% margin (Cost: {format_currency(product.cost, currency_code)}, Price: {format_currency(product.price, currency_code)})\n"

                context += "\n" + value_info
                logger.info(f"Added value information: {len(value_info)} chars")

        # Check for sales and analytics queries
        analytics_keywords = ["sales", "revenue", "analytics", "selling", "performance", "sold",
                             "purchase", "transaction", "customer", "buyer"]

        if any(keyword in user_message for keyword in analytics_keywords):
            sales_info = InventoryContext.get_sales_analytics(user=user)
            context += "\n\n" + sales_info
            logger.info(f"Added sales analytics: {len(sales_info)} chars")

        # Check for category-specific queries
        category_keywords = ["category", "categories", "group", "classification", "type"]
        category_query = None

        if any(keyword in user_message for keyword in category_keywords):
            # Try to extract category name from query
            if user:
                all_categories = Category.objects.filter(user=user)
            else:
                all_categories = Category.objects.all()

            category_names = [c.name.lower() for c in all_categories]

            # Check if any category name is mentioned in the query
            for name in category_names:
                if name in user_message:
                    category_query = name
                    logger.info(f"Found specific category in query: {category_query}")
                    break

            # If specific category found, get products in that category
            if category_query:
                if user:
                    category = Category.objects.filter(name__icontains=category_query, user=user).first()
                else:
                    category = Category.objects.filter(name__icontains=category_query).first()

                if category:
                    category_products = Product.objects.filter(category=category)

                    # Get user's currency preference if available
                    currency_code = 'USD'  # Default
                    if user and hasattr(user, 'profile'):
                        try:
                            currency_code = user.profile.currency
                        except Exception as e:
                            logger.error(f"Error getting user currency: {str(e)}")

                    category_info = f"\nProducts in Category '{category.name}':\n"
                    for product in category_products:
                        category_info += f"- {product.name}: {product.quantity} in stock, {format_currency(product.price, currency_code)}\n"

                    context += "\n" + category_info
                    logger.info(f"Added category products: {len(category_info)} chars")
            else:
                # If no specific category, list all categories with counts
                if user:
                    categories = Category.objects.filter(user=user)
                else:
                    categories = Category.objects.all()

                if categories.exists():
                    category_info = "\nAll Categories:\n"
                    for category in categories:
                        product_count = Product.objects.filter(category=category).count()
                        category_info += f"- {category.name}: {product_count} products\n"

                    context += "\n" + category_info
                    logger.info(f"Added all categories: {len(category_info)} chars")

        logger.info(f"Total context size: {len(context)} chars")
        return context
