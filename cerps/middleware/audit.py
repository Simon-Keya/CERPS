import logging
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        user_info = user.username if user and user.is_authenticated else 'Anonymous'
        logger.info(f"[{datetime.now()}] Request: {request.method} {request.path} by {user_info}")
