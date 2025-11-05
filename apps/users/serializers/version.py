from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import AppVersion


class AppVersionSerializer(serializers.ModelSerializer):
    """Serializer for AppVersion model"""

    class Meta:
        model = AppVersion
        fields = [
            'id',
            'version',
            'device_type',
            'is_active',
            'force_update',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate data before saving"""
        # Validation is handled in model's clean() method
        # But we can add additional API-level validation here if needed
        return data


class AppVersionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AppVersion"""

    class Meta:
        model = AppVersion
        fields = [
            'version',
            'device_type',
            'is_active',
            'force_update',
            'description'
        ]

    def validate(self, attrs):
        version = attrs.get('version')
        device_type = attrs.get('device_type')

        app_version = AppVersion.objects.filter(version=version, device_type=device_type)
        if app_version.exists():
            raise CustomException(message_key="VERSION_ALREADY_EXISTS")
        return attrs


class AppVersionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating AppVersion"""

    class Meta:
        model = AppVersion
        fields = [
            'version',
            'is_active',
            'force_update',
            'description',
            'device_type'
        ]
        # All fields are optional for updates
        extra_kwargs = {
            'version': {'required': False},
            'is_active': {'required': False},
            'force_update': {'required': False},
            'description': {'required': False},
            'device_type': {'required': False},
        }


class ActiveVersionSerializer(serializers.ModelSerializer):
    """Simplified serializer for active versions"""

    class Meta:
        model = AppVersion
        fields = ['id', 'version', 'device_type', 'force_update']
