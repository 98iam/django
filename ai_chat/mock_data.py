"""
Mock data provider for testing the AI chat feature when database access is not available.
This allows the AI to respond with sample inventory data even if the database is empty or inaccessible.
"""

def get_mock_inventory_summary():
    """
    Get a mock inventory summary for testing.
    """
    return """
Inventory Summary (SAMPLE DATA):
Total Products: 25
Total Categories: 5
Total Items in Stock: 342
Low Stock Items (<=10): 3
Out of Stock Items: 1

Sample Products:
- Gaming Mouse: 45 in stock, $59.99
- Mechanical Keyboard: 32 in stock, $89.99
- Gaming Headset: 28 in stock, $79.99
- Gaming Monitor: 15 in stock, $299.99
- Gaming Chair: 8 in stock, $199.99

Top Categories:
- Gaming Peripherals: 12 products
- Computer Components: 8 products
- Office Equipment: 3 products
- Networking: 2 products
"""

def get_mock_product_info():
    """
    Get mock product information for testing.
    """
    return """
Product Information (SAMPLE DATA):
- Gaming Mouse (SKU: GM001)
  Category: Gaming Peripherals
  Price: $59.99
  In Stock: 45
  Status: In Stock

- Mechanical Keyboard (SKU: KB001)
  Category: Gaming Peripherals
  Price: $89.99
  In Stock: 32
  Status: In Stock

- Gaming Headset (SKU: HS001)
  Category: Gaming Peripherals
  Price: $79.99
  In Stock: 28
  Status: In Stock

- Gaming Monitor (SKU: MON001)
  Category: Computer Components
  Price: $299.99
  In Stock: 15
  Status: In Stock

- Gaming Chair (SKU: CH001)
  Category: Office Equipment
  Price: $199.99
  In Stock: 8
  Status: Low Stock
"""

def get_mock_sales_analytics():
    """
    Get mock sales analytics for testing.
    """
    return """
Sales Analytics (SAMPLE DATA):
Total Sales: 156
Total Revenue: $12,450.85
Last 30 Days: 42 sales, $3,245.75 revenue

Top Selling Products:
- Gaming Mouse: 35 sales
- Mechanical Keyboard: 28 sales
- Gaming Headset: 22 sales
- Gaming Monitor: 15 sales
- Gaming Chair: 12 sales
"""
