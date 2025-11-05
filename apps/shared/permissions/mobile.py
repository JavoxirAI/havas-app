from rest_framework.permissions import BasePermission

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import Device


class IsMobileOrWebUser(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            return True
        token = request.headers.get('Token')
        if not token:
            raise CustomException(message_key="TOKEN_IS_NOT_PROVIDED")

        device = Device.objects.filter(device_token=token)
        request.device = device

        return device
