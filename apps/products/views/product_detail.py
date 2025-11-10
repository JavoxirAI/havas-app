from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.products.models import Product
from apps.products.serializers.product_list_create import (
    ProductDetailSerializer,
    ProductUpdateSerializer
)
from apps.shared.permissions.mobile import IsMobileOrWebUser
from apps.shared.utils.custom_response import CustomResponse


class ProductDetailRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET:    Retrieve product details
    PUT:    Update product
    PATCH:  Partial update product
    DELETE: Soft delete product (set is_active=False)
    """
    queryset = Product.objects.all()
    permission_classes = [IsMobileOrWebUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Return different serializers based on method"""
        if self.request.method in ['PUT', 'PATCH']:
            return ProductUpdateSerializer
        return ProductDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Get product detail"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def update(self, request, *args, **kwargs):
        """Update product"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )

        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductDetailSerializer(
                product,
                context={'request': request}
            )

            return CustomResponse.success(
                message_key="PRODUCT_UPDATED_SUCCESSFULLY",
                data=response_serializer.data,
                status_code=status.HTTP_200_OK,
                request=request
            )

        return CustomResponse.error(
            message_key="VALIDATION_ERROR",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            request=request
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete product"""
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])

        return CustomResponse.success(
            message_key="PRODUCT_DELETED_SUCCESSFULLY",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
            request=request
        )