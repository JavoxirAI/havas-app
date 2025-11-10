from rest_framework import serializers
from apps.contact.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'type', 'title', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_type(self, value):
        """Type validatsiyasi"""
        valid_types = ['phone', 'telegram', 'instagram', 'facebook', 'email']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid type. Must be one of: {', '.join(valid_types)}"
            )
        return value