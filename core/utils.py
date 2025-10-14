import logging
import json
from django.utils.timezone import now, localtime
from ipaddress import ip_address
from django.conf import settings

logger = logging.getLogger('core')

def log_event(event_type, request=None, user=None, extra=None):
    # Logs a structured event.
    # event_type: str, e.g., 'order_placed', 'login'
    # request: HttpRequest, optional
    # user: User instance, optional
    # extra: dict, any extra info

    timestamp = localtime(now()).strftime("%d/%m/%Y %H:%M:%S")
    log_data = {
        "timestamp": timestamp,  # IST timestamp
        "event": event_type,
        "user": getattr(user, "email", "Anonymous") if user else "Anonymous",
        "ip": get_client_ip(request) if request else None,
    }

    if extra:
        log_data.update(extra)

    logger.info(json.dumps(log_data, ensure_ascii=False))



def get_client_ip(request):
    # Returns the real client IP, ignoring trusted proxies.
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        for ip in ips:
            try:
                ip_obj = ip_address(ip)
                if not any(ip_obj in net for net in settings.TRUSTED_PROXIES):
                    return ip
            except ValueError:
                continue
        return ips[0]
    return request.META.get("REMOTE_ADDR")
