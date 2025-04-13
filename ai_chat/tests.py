from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category
from .inventory_context import InventoryContext

class InventoryContextTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create test categories associated with the user
        self.category1 = Category.objects.create(name='Electronics', user=self.user)
        self.category2 = Category.objects.create(name='Office Supplies', user=self.user)

        # Create test products associated with the user
        self.product1 = Product.objects.create(
            name='Gaming Mouse',
            description='High-performance gaming mouse',
            price=59.99,
            quantity=45,
            category=self.category1,
            sku='GM001',
            status='In Stock',
            user=self.user,
            cost=39.99  # Add cost field which is required
        )

        self.product2 = Product.objects.create(
            name='Office Chair',
            description='Ergonomic office chair',
            price=199.99,
            quantity=12,
            category=self.category2,
            sku='OC001',
            status='In Stock',
            user=self.user,
            cost=149.99  # Add cost field which is required
        )

        self.product3 = Product.objects.create(
            name='Keyboard',
            description='Mechanical keyboard',
            price=89.99,
            quantity=0,
            category=self.category1,
            sku='KB001',
            status='Out of Stock',
            user=self.user,
            cost=59.99  # Add cost field which is required
        )

    def test_get_product_info(self):
        # Test with specific query and user
        result = InventoryContext.get_product_info('mouse', user=self.user)
        self.assertIn('Gaming Mouse', result)
        self.assertIn('SKU: GM001', result)

        # Test with category query and user
        result = InventoryContext.get_product_info('Electronics', user=self.user)
        self.assertIn('Gaming Mouse', result)
        self.assertIn('Keyboard', result)

        # Test with non-existent product and user
        result = InventoryContext.get_product_info('nonexistent', user=self.user)
        self.assertIn('No products found', result)

    def test_get_inventory_summary(self):
        # Test with user
        result = InventoryContext.get_inventory_summary(user=self.user)
        self.assertIn('Total Products: 3', result)
        self.assertIn('Total Categories: 2', result)
        self.assertIn('Out of Stock Items: 1', result)

    def test_get_relevant_context(self):
        # Test product query with user
        result = InventoryContext.get_relevant_context('How many gaming mouse do we have in stock?', user=self.user)
        self.assertIn('Gaming Mouse', result)

        # Test inventory summary query with user
        result = InventoryContext.get_relevant_context('Give me an inventory summary', user=self.user)
        self.assertIn('Inventory Summary', result)

        # Test with no relevant context but with user
        # Note: This will now return inventory summary as we changed the implementation
        result = InventoryContext.get_relevant_context('Hello, how are you today?', user=self.user)
        self.assertIn('Inventory Summary', result)
