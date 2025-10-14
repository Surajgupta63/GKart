from .utils import log_event

class LogUserActivityMiddleware:
    """
    Logs only meaningful page views (optional) in production.
    Avoid logging every single click.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Example: log only important paths
        important_paths = ["/checkout/", "/cart/", "/accounts/login/"]
        if any(request.path.startswith(p) for p in important_paths):
            log_event(
                event_type="page_view",
                request=request,
                user=request.user
            )

        return response
