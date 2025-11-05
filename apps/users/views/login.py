# apps/users/views.py

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user import LoginSerializer, UserResponseSerializer


class LoginView(APIView):
    """
    Login view that returns JWT tokens
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate tokens
            tokens = user.get_tokens()

            # Serialize user data
            user_data = UserResponseSerializer(user).data

            return Response({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': user_data,
                    'tokens': tokens
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
