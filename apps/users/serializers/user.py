# apps/users/serializers.py

from rest_framework import serializers

from apps.users.models.user import User


class LoginSerializer(serializers.Serializer):
    """
    Flexible login serializer - accepts email, username, or phone_number
    """
    identifier = serializers.CharField(
        required=True,
        help_text="Email, username, or phone number"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError('Both identifier and password are required.')

        # Try to find user by email, username, or phone_number
        user = None
        try:
            # Try email first
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            # Try phone number
            elif identifier.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                user = User.objects.get(phone_number=identifier)
            # Try username
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials.')

        # Check password
        if user and not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials.')

        # Check if user is active
        if user and not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for user data in response"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number',
            'first_name', 'last_name', 'middle_name',
            'full_name', 'is_staff', 'is_superuser',
            'is_email_verified', 'is_phone_verified',
            'date_of_birth', 'created_at'
        ]
        read_only_fields = fields
