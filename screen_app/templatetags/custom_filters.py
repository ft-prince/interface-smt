from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    try:
        return lst[index]
    except (IndexError, TypeError):
        return None


    
@register.filter
def average(value):
    """Calculate the average of a list of values"""
    if not value or not isinstance(value, (list, tuple)):
        return 0
    return sum(value) / len(value)

@register.filter
def max_minus_min(value):
    """Calculate the range (max - min) of a list of values"""
    if not value or not isinstance(value, (list, tuple)):
        return 0
    try:
        return max(value) - min(value)
    except (TypeError, ValueError):
        return 0



from django import template
import operator

register = template.Library()

@register.filter
def avg_calc(value):
    """Calculate the average of a list of values"""
    if not value:
        return 0
    try:
        return sum(value) / len(value)
    except (TypeError, ValueError):
        return 0

@register.filter
def get_max(value, arg):
    """Return the maximum of two values"""
    try:
        return max(float(value), float(arg))
    except (TypeError, ValueError):
        return 0

@register.filter
def get_min(value, arg):
    """Return the minimum of two values"""
    try:
        return min(float(value), float(arg))
    except (TypeError, ValueError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return 0
    
    


    
@register.filter
def getattribute(obj, attr):
    """Gets an attribute of an object dynamically from a string."""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return ""
    