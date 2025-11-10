# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework import status
# from rest_framework.reverse import reverse_lazy
# from rest_framework.test import APITestCase
#
#
# class TestProductCreate(APITestCase):
#     def setUp(self):
#         self.url = reverse_lazy('products:list-create')
#         image_path = "/Users/sanjarbek/Developer/NajotTalim/havas/media/products/image.jpg"
#         with open(image_path, "rb") as img:
#             image_file = SimpleUploadedFile("image.jpg", img.read(), content_type="image/jpeg")
#
#         self.payload = {
#             "title": "Organic Honey",
#             "description": "Pure organic honey collected from mountain hives.",
#             "discount": 10,
#             "price": "25000.00",
#             "category": "BREAKFAST",
#             "measurement_type": "L",
#             "is_active": True,
#             "image": image_file,
#         }
#
#     def test_create_product_success(self):
#         response = self.client.post(path=self.url, data=self.payload, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.json().get('data').get('title'), "Organic Honey")
#
#     def test_check_discount_calculation(self):
#         pass
#
#     def test_missing_required_fields(self):
#         pass
#
#     def test_duplication_fields(self):
#         pass
#
#     def test_invalid_payload(self):
#         pass
#
#     def test_category_type(self):
#         pass
#
#     def test_measurement_type(self):
#         pass
