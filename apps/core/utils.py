from django.utils import timezone
from .models import AuditLog

def log_action(user, action, details=None):
    """
    Log an action to AuditLog.
    
    Args:
        user: The user performing the action (instance of users.User).
        action: A string describing the action (e.g., 'created_ledger').
        details: Optional dictionary with additional details.
    """
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details or {},
        timestamp=timezone.now()
    )