from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.products.models import Product
from apps.products.serializers.product_list_create import (
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer
)
from apps.shared.permissions.mobile import IsMobileOrWebUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class ProductListCreateApiView(ListCreateAPIView):
    """
    API endpoint for listing and creating products

    GET:  List all active products (paginated)
    POST: Create a new product with images (form-data or JSON)
    """
    serializer_class = ProductCreateSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsMobileOrWebUser]

    # ✅ Rasm yuklash uchun parser'lar
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Return only active products"""
        return Product.objects.filter(is_active=True).select_related(
            # Agar foreign key'lar bo'lsa qo'shing
        ).prefetch_related(
            'media_files'  # Rasmlarni oldindan yuklash (optimize)
        )

    def get_serializer_class(self):
        """
        Return different serializers based on request method and device type

        POST: ProductCreateSerializer (for creating)
        GET (WEB): ProductListSerializer (without translations)
        GET (MOBILE): ProductDetailSerializer (with translations)
        """
        if self.request.method == "POST":
            return ProductCreateSerializer
        elif self.request.method == "GET" and self.request.device_type == "WEB":
            return ProductListSerializer
        else:
            return ProductDetailSerializer

    def list(self, request, *args, **kwargs):
        """
        List products with pagination
        """
        queryset = self.filter_queryset(
            self.get_queryset().order_by('-id')
        )

        # Debug info
        print(f"Language: {request.lang}, Device: {request.device_type}")

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        # Agar pagination yo'q bo'lsa
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new product with images

        Accepts:
        - form-data (with file uploads)
        - JSON (with base64 images or without images)
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            # Save product
            product = serializer.save()

            # Return detailed response
            response_serializer = ProductDetailSerializer(
                product,
                context={'request': request}
            )

            return CustomResponse.success(
                message_key="PRODUCT_CREATED_SUCCESSFULLY",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
                request=request
            )
        else:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

    def get_paginated_response(self, data):
        """
        Custom paginated response format
        """
        assert self.paginator is not None
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data={
                'results': data,
                'pagination': {
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'page_size': self.paginator.page_size,
                    'current_page': self.paginator.page.number,
                    'total_pages': self.paginator.page.paginator.num_pages,
                }
            },
            status_code=status.HTTP_200_OK,
            request=self.request
        )