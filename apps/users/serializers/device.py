from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import Device


class DeviceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'device_model', 'operation_version', 'device_type',
            'device_id', 'ip_address', 'app_version', 'firebase_token',
            'language', 'theme'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate_device_model(self, device_model):
        "iPhone <script>alert('xss')</script>"
        if 'script' in device_model:
            raise CustomException(message_key='NOT_CREATED')
        return device_model
