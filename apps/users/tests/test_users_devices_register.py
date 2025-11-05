from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from apps.users.models.device import AppVersion, DeviceType, Device


class DeviceRegisterApiTestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.url = reverse_lazy('users:device-register')
        self.app_version = AppVersion.objects.create(
            version="1.0.0",
            force_update=False,
            device_type=DeviceType.ALL,
            is_active=True
        )
        self.base_payload = {
            "device_model": "iPhone 15 Pro",
            "operation_version": "iOS 18.1",
            "device_type": "IOS",
            "device_id": "F2B5E1C8-1C44-4F9D-9B99-ABF0D1C021212",
            "ip_address": "45.85.12.101",
            "language": "EN",
            "theme": "LIGHT",
            "app_version": self.app_version.id,
            "firebase_token": "fcm_token_12345_ios_examp12121"
        }

    def test_device_register_success(self):
        """Test successful device registration"""
        response = self.client.post(path=self.url, data=self.base_payload)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('device_token', response.json().get('data'))
        self.assertTrue(Device.objects.filter(device_id=self.base_payload['device_id']).exists())
