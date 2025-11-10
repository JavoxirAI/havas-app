# apps/users/serializers.py
from django.contrib.auth.password_validation import validate_password
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


class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone_number',
            'first_name', 'last_name', 'middle_name',
            'password', 'password_confirm',
            'date_of_birth'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        # Parollar bir xil ekanini tekshirish
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Passwords don't match."
            })

        # Email unique ekanini tekshirish
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                "email": "Email already exists."
            })

        # Username unique ekanini tekshirish
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                "username": "Username already exists."
            })

        # Telefon raqam unique ekanini tekshirish (agar berilgan bo'lsa)
        phone_number = attrs.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({
                "phone_number": "Phone number already exists."
            })

        return attrs

    def create(self, validated_data):
        # password_confirm ni olib tashlaymiz
        validated_data.pop('password_confirm')

        # User yaratish
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
        )

        return user
