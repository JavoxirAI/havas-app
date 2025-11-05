from rest_framework import status
from rest_framework.generics import ListCreateAPIView

from apps.products.models import Product
from apps.products.serializers.product_list_create import ProductCreateSerializer, ProductDetailSerializer, \
    ProductListSerializer
from apps.shared.permissions.mobile import IsMobileOrWebUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class ProductListCreateApiView(ListCreateAPIView):
    serializer_class = ProductCreateSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsMobileOrWebUser]

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateSerializer
        elif self.request.method == "GET" and self.request.device_type == "WEB":
            return ProductListSerializer
        else:
            return ProductDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by('-id'))
        print(request.lang, request.device_type, "********")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
                request=request
            )

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductDetailSerializer(product, context={'request': request})
            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors
            )
