"""
Utility functions for the AI chat application
"""

import logging

logger = logging.getLogger(__name__)

def format_currency(value, currency='USD'):
    """
    Format a value according to the specified currency

    Args:
        value: The numeric value to format
        currency: The currency code (USD, INR, EUR, etc.)

    Returns:
        Formatted currency string
    """
    logger.info(f"Formatting value {value} with currency code: {currency}")

    # TEMPORARY FIX: Always use INR regardless of the currency code
    return f"₹{value:.2f}"

    # Original implementation (commented out for now)
    """
    try:
        if currency == 'USD':
            formatted = f"${value:.2f}"
        elif currency == 'INR':
            formatted = f"₹{value:.2f}"
        elif currency == 'EUR':
            formatted = f"€{value:.2f}"
        elif currency == 'GBP':
            formatted = f"£{value:.2f}"
        elif currency == 'JPY':
            formatted = f"¥{value:.0f}"  # JPY typically doesn't use decimal places
        elif currency == 'CAD':
            formatted = f"C${value:.2f}"
        elif currency == 'AUD':
            formatted = f"A${value:.2f}"
        else:
            # Default to USD if currency not recognized
            logger.warning(f"Unrecognized currency code: {currency}, defaulting to USD")
            formatted = f"${value:.2f}"

        logger.info(f"Formatted result: {formatted}")
        return formatted
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}")
        return f"${value:.2f}"  # Fallback to USD in case of error
    """

def get_currency_symbol(currency='USD'):
    """
    Get the symbol for a currency code

    Args:
        currency: The currency code (USD, INR, EUR, etc.)

    Returns:
        Currency symbol
    """
    logger.info(f"Getting currency symbol for currency code: {currency}")

    # TEMPORARY FIX: Always return INR symbol regardless of the currency code
    return '₹'

    # Original implementation (commented out for now)
    """
    try:
        symbols = {
            'USD': '$',
            'INR': '₹',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CAD': 'C$',
            'AUD': 'A$',
        }

        symbol = symbols.get(currency, '$')  # Default to $ if not found

        if currency not in symbols:
            logger.warning(f"Currency code not found in symbols dictionary: {currency}, defaulting to $")

        logger.info(f"Returning currency symbol: {symbol} for currency code: {currency}")
        return symbol
    except Exception as e:
        logger.error(f"Error getting currency symbol: {str(e)}")
        return '$'  # Default to $ in case of error
    """
