from django.shortcuts import render


class CustomErrorMiddleware:
    """
    Middleware to render custom error pages for additional status codes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        custom_error_codes = [401, 405, 410, 429, 502, 503, 504]
        if response.status_code in custom_error_codes:
            template_name = f"{response.status_code}.html"
            return render(request, template_name, status=response.status_code)

        return response
