from django.urls import path

from apps.products.views.product_detail import ProductDetailRetrieveUpdateDestroyAPIView
from apps.products.views.product_list_create import ProductListCreateApiView

app_name = 'products'

urlpatterns = [
    path('', ProductListCreateApiView.as_view(), name='list-create'),
    path('<int:pk>/', ProductDetailRetrieveUpdateDestroyAPIView.as_view(), name='detail'),
]
