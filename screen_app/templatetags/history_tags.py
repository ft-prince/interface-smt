# screen_app/templatetags/history_tags.py
from django import template

register = template.Library()

@register.filter
def get_model_name(history_record):
    """
    Returns the verbose name of the model for a historical record.
    """
    return history_record.instance._meta.verbose_name.title()