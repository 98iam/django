"""
Utility functions for the AI chat application
"""

def format_currency(value, currency='USD'):
    """
    Format a value according to the specified currency
    
    Args:
        value: The numeric value to format
        currency: The currency code (USD, INR, EUR, etc.)
        
    Returns:
        Formatted currency string
    """
    if currency == 'USD':
        return f"${value:.2f}"
    elif currency == 'INR':
        return f"₹{value:.2f}"
    elif currency == 'EUR':
        return f"€{value:.2f}"
    elif currency == 'GBP':
        return f"£{value:.2f}"
    elif currency == 'JPY':
        return f"¥{value:.0f}"  # JPY typically doesn't use decimal places
    elif currency == 'CAD':
        return f"C${value:.2f}"
    elif currency == 'AUD':
        return f"A${value:.2f}"
    else:
        # Default to USD if currency not recognized
        return f"${value:.2f}"

def get_currency_symbol(currency='USD'):
    """
    Get the symbol for a currency code
    
    Args:
        currency: The currency code (USD, INR, EUR, etc.)
        
    Returns:
        Currency symbol
    """
    symbols = {
        'USD': '$',
        'INR': '₹',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    return symbols.get(currency, '$')  # Default to $ if not found
