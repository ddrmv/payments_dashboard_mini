from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key."""
    return dictionary.get(key, key)


@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def currency_format(value, decimal_places=2):
    """Format a number as currency with comma separators and decimal places."""
    try:
        num = float(value)
        # Format with comma separators and specified decimal places
        formatted = f"{num:,.{decimal_places}f}"
        return formatted
    except (ValueError, TypeError):
        return "0.00"
