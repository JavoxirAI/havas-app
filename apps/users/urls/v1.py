from django.urls import path

from apps.users.views.device import DeviceRegisterCreateAPIView, DeviceListApiView
from apps.users.views.login import LoginView, RegisterView

app_name = 'users'

urlpatterns = [
    path('devices/', DeviceRegisterCreateAPIView.as_view(), name='device-register'),
    path('devices/list/', DeviceListApiView.as_view(), name='device-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]
