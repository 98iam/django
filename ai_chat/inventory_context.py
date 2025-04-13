from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import logging

# Import mock data for fallback
from .mock_data import get_mock_inventory_summary, get_mock_product_info, get_mock_sales_analytics

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
            return get_mock_product_info()

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

            # Limit results
            products = products[:limit]
            product_list = list(products)  # Force evaluation of the queryset

            if not product_list:
                if query:
                    return f"No products found matching '{query}'."
                else:
                    return "No products found in the inventory."

            # Format product information
            result = "Product Information:\n"
            for product in product_list:
                result += f"- {product.name} (SKU: {product.sku})\n"
                result += f"  Category: {product.category.name if product.category else 'Uncategorized'}\n"
                result += f"  Price: ${product.price}\n"
                result += f"  In Stock: {product.quantity}\n"
                result += f"  Status: {product.status}\n"
                result += "\n"

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
            return get_mock_inventory_summary()

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

            total_stock = products.aggregate(total=Sum('quantity'))['total'] or 0
            low_stock = products.filter(quantity__lte=10).count()
            out_of_stock = products.filter(quantity=0).count()

            # Get some sample products to show
            sample_products = list(products[:5])

            # Build the summary
            result = "Inventory Summary:\n"
            result += f"Total Products: {total_products}\n"
            result += f"Total Categories: {total_categories}\n"
            result += f"Total Items in Stock: {total_stock}\n"
            result += f"Low Stock Items (<=10): {low_stock}\n"
            result += f"Out of Stock Items: {out_of_stock}\n\n"

            # Add sample products
            if sample_products:
                result += "Sample Products:\n"
                for product in sample_products:
                    result += f"- {product.name}: {product.quantity} in stock, ${product.price}\n"
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
                        result += "Top Categories:\n"
                        for category in category_list:
                            result += f"- {category.name}: {category.product_count} products\n"
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
            return get_mock_sales_analytics()

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

            # Get recent sales (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_sales = sales.filter(sale_date__gte=thirty_days_ago)
            recent_count = recent_sales.count()
            recent_revenue = recent_sales.aggregate(total=Sum('total_amount'))['total'] or 0

            # Build the result
            result = "Sales Analytics:\n"
            result += f"Total Sales: {total_sales}\n"
            result += f"Total Revenue: ${total_revenue}\n"
            result += f"Last 30 Days: {recent_count} sales, ${recent_revenue} revenue\n\n"

            # Try to get top selling products
            try:
                if user:
                    # Get top selling products for this user only
                    top_products = Product.objects.filter(user=user).annotate(
                        sale_count=Count('sale_items')
                    ).order_by('-sale_count')[:5]
                else:
                    # Get top selling products across all users
                    top_products = Product.objects.annotate(
                        sale_count=Count('sale_items')
                    ).order_by('-sale_count')[:5]

                product_list = list(top_products)  # Force evaluation

                if product_list:
                    result += "Top Selling Products:\n"
                    for product in product_list:
                        result += f"- {product.name}: {product.sale_count} sales\n"
            except Exception as product_error:
                logger.error(f"Error getting top products: {str(product_error)}")
                result += "\nNote: Unable to retrieve top selling products.\n"

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

        Returns:
            Formatted string with relevant context
        """
        if not MODELS_AVAILABLE:
            logger.warning("Models not available when getting context, using mock data")
            # Use mock data instead of returning an error
            context = get_mock_inventory_summary()
            context += "\n\n" + get_mock_product_info()
            return context

        # Always include inventory summary for any question about products or inventory
        # This ensures the AI has context about the inventory regardless of the specific question
        context = InventoryContext.get_inventory_summary(user=user)

        user_message = user_message.lower()
        logger.info(f"Getting context for message: {user_message}")

        # Check for product-specific queries
        product_keywords = ["product", "item", "stock", "price", "sku", "quantity"]
        if any(keyword in user_message for keyword in product_keywords):
            # For product queries, don't try to extract a specific product name yet
            # Just return all products (limited to 10) to give the AI context
            product_info = InventoryContext.get_product_info(user=user)
            context += "\n" + product_info
            logger.info(f"Added product info: {len(product_info)} chars")

        # Check for sales and analytics queries
        analytics_keywords = ["sales", "revenue", "analytics", "selling", "performance"]
        if any(keyword in user_message for keyword in analytics_keywords):
            sales_info = InventoryContext.get_sales_analytics(user=user)
            context += "\n" + sales_info
            logger.info(f"Added sales analytics: {len(sales_info)} chars")

        logger.info(f"Total context size: {len(context)} chars")
        return context
