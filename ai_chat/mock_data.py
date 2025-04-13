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

Stock Status:
Normal Stock Items: 21
Low Stock Items (<=10): 3
Out of Stock Items: 1
Overstocked Items: 0

Financial Metrics:
Total Inventory Value: $28,456.75
Total Inventory Cost: $17,890.25
Total Potential Profit: $10,566.50
Average Profit Margin: 42.5%

Inventory Timeline:
Oldest Product: Gaming Mouse (Added: 2023-01-15)
Newest Product: Gaming Chair (Added: 2023-12-05)

Sample Products:
- Gaming Mouse: 45 in stock, $59.99 each, total value: $2,699.55
- Mechanical Keyboard: 32 in stock, $89.99 each, total value: $2,879.68
- Gaming Headset: 28 in stock, $79.99 each, total value: $2,239.72
- Gaming Monitor: 15 in stock, $299.99 each, total value: $4,499.85
- Gaming Chair: 8 in stock, $199.99 each, total value: $1,599.92

Categories:
- Gaming Peripherals: 12 products, 105 items, value: $8,819.95
- Computer Components: 8 products, 87 items, value: $12,456.80
- Office Equipment: 3 products, 15 items, value: $3,999.85
- Networking: 2 products, 35 items, value: $3,180.15
"""

def get_mock_product_info():
    """
    Get mock product information for testing.
    """
    return """
Product Information (SAMPLE DATA):
- Gaming Mouse (SKU: GM001)
  Description: High-performance gaming mouse with RGB lighting and programmable buttons
  Category: Gaming Peripherals
  Price: $59.99
  Cost: $35.99
  Profit Margin: 66.69%
  In Stock: 45
  Total Value: $2,699.55
  Potential Profit: $1,080.00
  Minimum Stock: 10
  Maximum Stock: 50
  Stock Status: Normal
  Location: Warehouse A, Shelf 3
  Supplier: Gaming Gear Inc.
  Created: 2023-01-15
  Last Updated: 2023-11-20
  Status: active

- Mechanical Keyboard (SKU: KB001)
  Description: Mechanical gaming keyboard with Cherry MX switches and customizable backlighting
  Category: Gaming Peripherals
  Price: $89.99
  Cost: $52.50
  Profit Margin: 71.41%
  In Stock: 32
  Total Value: $2,879.68
  Potential Profit: $1,199.68
  Minimum Stock: 8
  Maximum Stock: 40
  Stock Status: Normal
  Location: Warehouse A, Shelf 2
  Supplier: Gaming Gear Inc.
  Created: 2023-02-10
  Last Updated: 2023-10-15
  Status: active

- Gaming Headset (SKU: HS001)
  Description: Surround sound gaming headset with noise-cancelling microphone
  Category: Gaming Peripherals
  Price: $79.99
  Cost: $45.00
  Profit Margin: 77.76%
  In Stock: 28
  Total Value: $2,239.72
  Potential Profit: $979.72
  Minimum Stock: 5
  Maximum Stock: 30
  Stock Status: Normal
  Location: Warehouse A, Shelf 4
  Supplier: Audio Tech Ltd.
  Created: 2023-03-22
  Last Updated: 2023-11-05
  Status: active

- Gaming Monitor (SKU: MON001)
  Description: 27-inch 4K gaming monitor with 144Hz refresh rate and 1ms response time
  Category: Computer Components
  Price: $299.99
  Cost: $210.00
  Profit Margin: 42.85%
  In Stock: 15
  Total Value: $4,499.85
  Potential Profit: $1,349.85
  Minimum Stock: 3
  Maximum Stock: 20
  Stock Status: Normal
  Location: Warehouse B, Shelf 1
  Supplier: Display Solutions
  Created: 2023-06-15
  Last Updated: 2023-12-01
  Status: active

- Gaming Chair (SKU: CH001)
  Description: Ergonomic gaming chair with adjustable armrests and lumbar support
  Category: Office Equipment
  Price: $199.99
  Cost: $120.00
  Profit Margin: 66.66%
  In Stock: 8
  Total Value: $1,599.92
  Potential Profit: $639.92
  Minimum Stock: 5
  Maximum Stock: 15
  Stock Status: Low Stock
  Location: Warehouse C, Shelf 2
  Supplier: Comfort Seating Co.
  Created: 2023-12-05
  Last Updated: 2023-12-05
  Status: active

Product Age Information:
Oldest Product: Gaming Mouse (Created: 2023-01-15)
Newest Product: Gaming Chair (Created: 2023-12-05)
"""

def get_mock_sales_analytics():
    """
    Get mock sales analytics for testing.
    """
    return """
Sales Analytics (SAMPLE DATA):
Total Sales: 156
Total Revenue: $12,450.85
Average Sale Value: $79.81

Time-Based Analytics:
Today: 3 sales, $245.97 revenue
Last 7 Days: 18 sales, $1,456.25 revenue
Last 30 Days: 42 sales, $3,245.75 revenue
First Sale: 2023-01-20
Latest Sale: 2023-12-10

Payment Methods:
- Credit Card: 98 sales (62.8%)
- Cash: 35 sales (22.4%)
- Bank Transfer: 18 sales (11.5%)
- Other: 5 sales (3.2%)

Top Selling Products:
- Gaming Mouse: 35 sales, $2,099.65 revenue
- Mechanical Keyboard: 28 sales, $2,519.72 revenue
- Gaming Headset: 22 sales, $1,759.78 revenue
- Gaming Monitor: 15 sales, $4,499.85 revenue
- Gaming Chair: 12 sales, $2,399.88 revenue

Top Products by Revenue:
- Gaming Monitor: $4,499.85 revenue, 15 sales
- Gaming Chair: $2,399.88 revenue, 12 sales
- Mechanical Keyboard: $2,519.72 revenue, 28 sales
- Gaming Mouse: $2,099.65 revenue, 35 sales
- Gaming Headset: $1,759.78 revenue, 22 sales

Top Categories by Revenue:
- Computer Components: $6,589.75 revenue, 25 sales
- Gaming Peripherals: $6,379.15 revenue, 85 sales
- Office Equipment: $2,399.88 revenue, 12 sales
"""
