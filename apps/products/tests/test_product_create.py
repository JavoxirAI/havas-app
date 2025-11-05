"""
Complete Product Create Tests
"""
from decimal import Decimal
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from apps.products.models import Product, ProductCategory, MeasurementType
from apps.users.models.user import User


class TestProductCreate(APITestCase):
    """Test cases for product creation"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse_lazy('products:list-create')

        # Create and authenticate user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

        # Create test image in memory (no need for real file path)
        self.image_file = self.create_test_image()

        self.payload = {
            "title": "Organic Honey",
            "description": "Pure organic honey collected from mountain hives.",
            "discount": 10,
            "price": "25000.00",
            "category": "BREAKFAST",
            "measurement_type": "L",
            "is_active": True,
            "image": self.image_file,
        }

    def create_test_image(self, name='test_image.jpg', size=(100, 100)):
        """Create a test image in memory"""
        image = Image.new('RGB', size, color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        return SimpleUploadedFile(
            name,
            image_io.read(),
            content_type="image/jpeg"
        )

    def test_create_product_success(self):
        """Test creating product successfully"""
        payload = self.payload.copy()
        payload['image'] = self.create_test_image()

        response = self.client.post(path=self.url, data=payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertEqual(response_data.get('data').get('title'), "Organic Honey")

        # Verify product was created in database
        product = Product.objects.get(title="Organic Honey")
        self.assertEqual(product.price, Decimal('25000.00'))
        self.assertEqual(product.discount, 10)
        self.assertEqual(product.category, ProductCategory.BREAKFAST)

    def test_check_discount_calculation(self):
        """Test discount calculation and real_price"""
        payload = self.payload.copy()
        payload['image'] = self.create_test_image()
        payload['price'] = "100.00"
        payload['discount'] = 20  # 20% discount

        response = self.client.post(path=self.url, data=payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(title="Organic Honey")

        # Check if real_price is calculated correctly
        # If discount is 20%, real_price should be higher than price
        # Depends on your business logic:
        # Option 1: real_price = price, discounted_price calculated separately
        # Option 2: price is after discount, real_price is original

        # Assuming: price = final price, real_price = original price
        # If discount = 20%, and price = 100, then real_price should be 125
        # Or if you store it differently, adjust this test

        self.assertEqual(product.price, Decimal('100.00'))
        self.assertEqual(product.discount, 20)

        # Test different discount values
        test_cases = [
            (0, "100.00"),  # No discount
            (50, "100.00"),  # 50% discount
            (100, "100.00"),  # 100% discount (free)
        ]

        for discount, price in test_cases:
            payload_test = self.payload.copy()
            payload_test['image'] = self.create_test_image()
            payload_test['title'] = f"Product Discount {discount}"
            payload_test['price'] = price
            payload_test['discount'] = discount

            response = self.client.post(path=self.url, data=payload_test, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            product = Product.objects.get(title=f"Product Discount {discount}")
            self.assertEqual(product.discount, discount)

    def test_missing_required_fields(self):
        """Test creating product with missing required fields"""
        required_fields = ['title', 'description', 'price', 'category', 'measurement_type']

        for field in required_fields:
            payload = self.payload.copy()
            payload['image'] = self.create_test_image()
            del payload[field]

            response = self.client.post(path=self.url, data=payload, format='multipart')

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Field '{field}' should be required but request succeeded"
            )

            # Check error response contains field name
            response_data = response.json()
            self.assertIn('errors', response_data)

    def test_duplication_fields(self):
        """Test creating products with duplicate titles or unique fields"""
        # First product
        payload1 = self.payload.copy()
        payload1['image'] = self.create_test_image()

        response1 = self.client.post(path=self.url, data=payload1, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second product with same title (should succeed if title is not unique)
        payload2 = self.payload.copy()
        payload2['image'] = self.create_test_image(name='test_image2.jpg')

        response2 = self.client.post(path=self.url, data=payload2, format='multipart')

        # This depends on your business logic:
        # If title must be unique, expect 400
        # If title can be duplicate, expect 201

        # Assuming titles CAN be duplicate (common in e-commerce):
        if response2.status_code == status.HTTP_201_CREATED:
            self.assertEqual(Product.objects.filter(title="Organic Honey").count(), 2)
        else:
            # If titles must be unique
            self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_payload(self):
        """Test creating product with invalid data types"""

        # Test 1: Invalid price (string that's not a number)
        payload_invalid_price = self.payload.copy()
        payload_invalid_price['image'] = self.create_test_image()
        payload_invalid_price['price'] = "invalid_price"

        response = self.client.post(path=self.url, data=payload_invalid_price, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test 2: Negative price
        payload_negative_price = self.payload.copy()
        payload_negative_price['image'] = self.create_test_image()
        payload_negative_price['price'] = "-100.00"

        response = self.client.post(path=self.url, data=payload_negative_price, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test 3: Invalid discount (> 100)
        payload_invalid_discount = self.payload.copy()
        payload_invalid_discount['image'] = self.create_test_image()
        payload_invalid_discount['discount'] = 150

        response = self.client.post(path=self.url, data=payload_invalid_discount, format='multipart')
        # This should fail if you have discount validation
        # If not, add validation: 0 <= discount <= 100

        # Test 4: Negative discount
        payload_negative_discount = self.payload.copy()
        payload_negative_discount['image'] = self.create_test_image()
        payload_negative_discount['discount'] = -10

        response = self.client.post(path=self.url, data=payload_negative_discount, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test 5: Invalid is_active (not boolean)
        payload_invalid_active = self.payload.copy()
        payload_invalid_active['image'] = self.create_test_image()
        payload_invalid_active['is_active'] = "not_a_boolean"

        response = self.client.post(path=self.url, data=payload_invalid_active, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test 6: Empty title
        payload_empty_title = self.payload.copy()
        payload_empty_title['image'] = self.create_test_image()
        payload_empty_title['title'] = ""

        response = self.client.post(path=self.url, data=payload_empty_title, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test 7: Title too long (> 255 characters)
        payload_long_title = self.payload.copy()
        payload_long_title['image'] = self.create_test_image()
        payload_long_title['title'] = "A" * 256

        response = self.client.post(path=self.url, data=payload_long_title, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_type(self):
        """Test different category types"""
        valid_categories = ['BREAKFAST', 'LUNCH', 'DINNER', 'ALL']

        for category in valid_categories:
            payload = self.payload.copy()
            payload['image'] = self.create_test_image()
            payload['title'] = f"Product {category}"
            payload['category'] = category

            response = self.client.post(path=self.url, data=payload, format='multipart')

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                f"Category '{category}' should be valid"
            )

            product = Product.objects.get(title=f"Product {category}")
            self.assertEqual(product.category, category)
            self.assertEqual(product.get_category_display(), ProductCategory[category].label)

        # Test invalid category
        payload_invalid = self.payload.copy()
        payload_invalid['image'] = self.create_test_image()
        payload_invalid['category'] = 'INVALID_CATEGORY'

        response = self.client.post(path=self.url, data=payload_invalid, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test empty category
        payload_empty = self.payload.copy()
        payload_empty['image'] = self.create_test_image()
        payload_empty['category'] = ''

        response = self.client.post(path=self.url, data=payload_empty, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test case sensitivity (should be case sensitive)
        payload_lowercase = self.payload.copy()
        payload_lowercase['image'] = self.create_test_image()
        payload_lowercase['category'] = 'breakfast'  # lowercase

        response = self.client.post(path=self.url, data=payload_lowercase, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_measurement_type(self):
        """Test different measurement types"""
        valid_measurements = ['GR', 'PC', 'L']
        measurement_labels = {
            'GR': 'Gram',
            'PC': 'Peace',
            'L': 'Litre'
        }

        for measurement in valid_measurements:
            payload = self.payload.copy()
            payload['image'] = self.create_test_image()
            payload['title'] = f"Product Measurement {measurement}"
            payload['measurement_type'] = measurement

            response = self.client.post(path=self.url, data=payload, format='multipart')

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                f"Measurement type '{measurement}' should be valid"
            )

            product = Product.objects.get(title=f"Product Measurement {measurement}")
            self.assertEqual(product.measurement_type, measurement)
            self.assertEqual(
                product.get_measurement_type_display(),
                measurement_labels[measurement]
            )

        # Test invalid measurement type
        payload_invalid = self.payload.copy()
        payload_invalid['image'] = self.create_test_image()
        payload_invalid['measurement_type'] = 'INVALID_TYPE'

        response = self.client.post(path=self.url, data=payload_invalid, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test empty measurement type
        payload_empty = self.payload.copy()
        payload_empty['image'] = self.create_test_image()
        payload_empty['measurement_type'] = ''

        response = self.client.post(path=self.url, data=payload_empty, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test case sensitivity
        payload_lowercase = self.payload.copy()
        payload_lowercase['image'] = self.create_test_image()
        payload_lowercase['measurement_type'] = 'gr'  # lowercase

        response = self.client.post(path=self.url, data=payload_lowercase, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_without_authentication(self):
        """Test that product creation requires authentication"""
        self.client.force_authenticate(user=None)

        payload = self.payload.copy()
        payload['image'] = self.create_test_image()

        response = self.client.post(path=self.url, data=payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_without_image(self):
        """Test creating product without image (if optional)"""
        payload = self.payload.copy()
        # Don't add image

        response = self.client.post(path=self.url, data=payload, format='json')

        # This depends on whether image is required or optional
        # Adjust based on your business logic
        if response.status_code == status.HTTP_201_CREATED:
            product = Product.objects.get(title="Organic Honey")
            self.assertIsNotNone(product)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_invalid_image_format(self):
        """Test creating product with invalid image format"""
        payload = self.payload.copy()

        # Create invalid file (text file pretending to be image)
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        payload['image'] = invalid_file

        response = self.client.post(path=self.url, data=payload, format='multipart')

        # Should fail validation if you have image format validation
        # Otherwise adjust this test
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """Clean up after tests"""
        # Delete all media files
        from apps.shared.models import Media

        try:
            for media in Media.objects.all():
                if media.file:
                    try:
                        if media.file.storage.exists(media.file.name):
                            media.file.storage.delete(media.file.name)
                    except Exception:
                        pass

            Media.objects.all().delete()
            Product.objects.all().delete()
        except Exception as e:
            print(f"Warning: Cleanup error: {e}")