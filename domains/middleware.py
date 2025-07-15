

from django.utils.deprecation import MiddlewareMixin

from .utils import get_allowed_domains

# from urllib.parse import urlparse


class CustomCORSValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        if not origin:
            return None  # Continue if no Origin header
        
        allowed_domains = get_allowed_domains()

        # parsed_url = urlparse(origin)
        # origin = parsed_url.netloc  # Returns 'localhost:3000' or 'example.com'

        # print(origin)
        if origin in allowed_domains:
            return None  # Allow the request
        
        # Reject non-matching origins (optional: customize the response)
        from django.http import JsonResponse
        print("Rejecting non-matching origins");
        return JsonResponse({'error': 'CORS not allowed'}, status=403)
