from typing import Any

from rest_framework import generics, permissions, status

from apps.shared.permissions.mobile import IsMobileOrWebUser
from apps.shared.utils.custom_response import CustomResponse
from apps.users.models.device import Device
from apps.users.serializers.device import DeviceRegisterSerializer


class DeviceRegisterCreateAPIView(generics.CreateAPIView):
    """
    Register device anonymously (no login required).
    Returns a device_token for future reference.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.device = None

    def perform_create(self, serializer):
        device = serializer.save()
        self.device = device

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data['device_token'] = str(self.device.device_token)
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=response.data,
            status_code=status.HTTP_201_CREATED
        )


class DeviceListApiView(generics.ListAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceRegisterSerializer
    permission_classes = [IsMobileOrWebUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data
        )
