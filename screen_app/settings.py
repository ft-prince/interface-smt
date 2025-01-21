# settings.py
from datetime import timedelta
from django.conf import settings

AUDIT_HISTORY_RETENTION_CHOICES = {
    '3m': {'days': 90, 'label': '3 Months'},
    '6m': {'days': 180, 'label': '6 Months'},
    '1y': {'days': 365, 'label': '1 Year'},
    '2y': {'days': 730, 'label': '2 Years'},
    '3y': {'days': 1095, 'label': '3 Years'},
    'all': {'days': None, 'label': 'All Time'}
}

# Default retention period
DEFAULT_AUDIT_RETENTION = getattr(settings, 'DEFAULT_AUDIT_RETENTION', '6m')