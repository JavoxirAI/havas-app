from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import Device


class AddCustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_token = request.headers.get('Token', None)
        if device_token:
            request.device_type = "MOBILE"
            try:
                device = Device.objects.get(device_token=device_token)
                request.lang = str(device.language).lower()
            except Device.DoesNotExist:
                raise CustomException(message_key="NOT_FOUND")

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header:
            request.device_type = "WEB"
            request.lang = request.headers.get('Accept-Language', 'uz')

        # Continue processing the request
        response = self.get_response(request)

        return response
