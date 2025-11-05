from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.story.models import Story, StoryView, StoryType, StoryStatus
from apps.story.serializers.serializers import (
    StoryCreateSerializer,
    StoryListSerializer,
    StoryDetailSerializer,
    StoryUpdateSerializer,
    StoryViewCreateSerializer,
    StoryPublicSerializer
)
from apps.users.models.user import User
from apps.users.models.device import Device, AppVersion, DeviceType


class StoryCreateSerializerTestCase(TestCase):
    """Test cases for StoryCreateSerializer"""

    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'title': 'New Product Launch',
            'description': 'Check out our latest product!',
            'story_type': 'PROMOTION',
            'status': 'PUBLISHED',
            'order': 1,
            'duration': 5,
            'is_active': True,
            'is_featured': False,
        }

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        serializer = StoryCreateSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.title, 'New Product Launch')
        self.assertEqual(story.story_type, StoryType.PROMOTION)
        self.assertEqual(story.status, StoryStatus.PUBLISHED)

    def test_serializer_with_missing_title(self):
        """Test serializer without title"""
        data = self.valid_data.copy()
        del data['title']

        serializer = StoryCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_with_invalid_duration(self):
        """Test serializer with invalid duration"""
        # Duration < 1
        data1 = self.valid_data.copy()
        data1['duration'] = 0

        serializer1 = StoryCreateSerializer(data=data1)
        self.assertFalse(serializer1.is_valid())
        self.assertIn('duration', serializer1.errors)

        # Duration > 30
        data2 = self.valid_data.copy()
        data2['duration'] = 31

        serializer2 = StoryCreateSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertIn('duration', serializer2.errors)

    def test_serializer_with_past_expiration_date(self):
        """Test serializer with past expiration date"""
        data = self.valid_data.copy()
        data['expires_at'] = (timezone.now() - timedelta(days=1)).isoformat()

        serializer = StoryCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('expires_at', serializer.errors)

    def test_serializer_expires_before_publish(self):
        """Test expiration date before publication date"""
        now = timezone.now()

        data = self.valid_data.copy()
        data['published_at'] = (now + timedelta(days=2)).isoformat()
        data['expires_at'] = (now + timedelta(days=1)).isoformat()

        serializer = StoryCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('expires_at', serializer.errors)

    def test_serializer_auto_set_published_at(self):
        """Test auto-setting published_at for PUBLISHED status"""
        data = self.valid_data.copy()
        # Don't set published_at

        serializer = StoryCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertIsNotNone(story.published_at)

    def test_serializer_with_optional_fields(self):
        """Test serializer with optional fields"""
        data = {
            'title': 'Simple Story',
            'story_type': 'NEWS',
            'status': 'DRAFT',
        }

        serializer = StoryCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.title, 'Simple Story')

    def test_serializer_with_action_url(self):
        """Test serializer with action URL"""
        data = self.valid_data.copy()
        data['action_url'] = 'https://example.com/product'

        serializer = StoryCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.action_url, 'https://example.com/product')

    def test_serializer_with_invalid_action_url(self):
        """Test serializer with invalid action URL"""
        data = self.valid_data.copy()
        data['action_url'] = 'not-a-url'

        serializer = StoryCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('action_url', serializer.errors)


class StoryListSerializerTestCase(TestCase):
    """Test cases for StoryListSerializer"""

    def setUp(self):
        """Set up test data"""
        self.story = Story.objects.create(
            title='Test Story',
            description='Test description',
            story_type=StoryType.PROMOTION,
            status=StoryStatus.PUBLISHED,
            is_active=True,
            order=1,
            duration=5
        )

    def test_serializer_contains_expected_fields(self):
        """Test serializer contains all expected fields"""
        serializer = StoryListSerializer(self.story)

        expected_fields = [
            'id', 'uuid', 'title', 'description', 'story_type',
            'status', 'order', 'duration', 'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url',
            'view_count', 'click_count', 'is_expired', 'is_published',
            'created_at', 'updated_at'
        ]

        for field in expected_fields:
            self.assertIn(field, serializer.data)

    def test_serializer_read_only_fields(self):
        """Test read-only fields"""
        serializer = StoryListSerializer(self.story)

        self.assertIn('is_expired', serializer.data)
        self.assertIn('is_published', serializer.data)

    def test_serializer_list_multiple_stories(self):
        """Test serializing multiple stories"""
        Story.objects.create(title='Story 2', story_type=StoryType.NEWS)
        Story.objects.create(title='Story 3', story_type=StoryType.FEATURED)

        stories = Story.objects.all()
        serializer = StoryListSerializer(stories, many=True)

        self.assertEqual(len(serializer.data), 3)


class StoryDetailSerializerTestCase(TestCase):
    """Test cases for StoryDetailSerializer"""

    def setUp(self):
        """Set up test data"""
        self.story = Story.objects.create(
            title='Test Story',
            description='Test description',
            story_type=StoryType.PROMOTION,
            status=StoryStatus.PUBLISHED,
            is_active=True
        )

    def test_serializer_contains_display_fields(self):
        """Test serializer contains display fields"""
        serializer = StoryDetailSerializer(self.story)

        self.assertIn('story_type_display', serializer.data)
        self.assertIn('status_display', serializer.data)

        self.assertEqual(serializer.data['story_type_display'], 'Promotion')
        self.assertEqual(serializer.data['status_display'], 'Published')

    def test_serializer_all_fields_present(self):
        """Test all fields are present"""
        serializer = StoryDetailSerializer(self.story)

        expected_fields = [
            'id', 'uuid', 'title', 'description',
            'story_type', 'story_type_display',
            'status', 'status_display',
            'order', 'duration',
            'published_at', 'expires_at',
            'is_active', 'is_featured', 'action_url',
            'view_count', 'click_count',
            'is_expired', 'is_published',
            'created_at', 'updated_at'
        ]

        for field in expected_fields:
            self.assertIn(field, serializer.data)


class StoryUpdateSerializerTestCase(TestCase):
    """Test cases for StoryUpdateSerializer"""

    def setUp(self):
        """Set up test data"""
        self.story = Story.objects.create(
            title='Original Title',
            description='Original description',
            story_type=StoryType.PROMOTION,
            status=StoryStatus.DRAFT,
            duration=5
        )

    def test_update_title(self):
        """Test updating title"""
        data = {'title': 'Updated Title'}

        serializer = StoryUpdateSerializer(self.story, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.title, 'Updated Title')

    def test_update_status(self):
        """Test updating status"""
        data = {'status': 'PUBLISHED'}

        serializer = StoryUpdateSerializer(self.story, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.status, StoryStatus.PUBLISHED)

    def test_update_multiple_fields(self):
        """Test updating multiple fields"""
        data = {
            'title': 'New Title',
            'description': 'New description',
            'is_featured': True
        }

        serializer = StoryUpdateSerializer(self.story, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertEqual(story.title, 'New Title')
        self.assertEqual(story.description, 'New description')
        self.assertTrue(story.is_featured)

    def test_update_with_invalid_duration(self):
        """Test updating with invalid duration"""
        data = {'duration': 50}

        serializer = StoryUpdateSerializer(self.story, data=data, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn('duration', serializer.errors)

    def test_partial_update(self):
        """Test partial update (PATCH)"""
        data = {'is_active': False}

        serializer = StoryUpdateSerializer(self.story, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        story = serializer.save()

        self.assertFalse(story.is_active)
        # Other fields should remain unchanged
        self.assertEqual(story.title, 'Original Title')


class StoryViewCreateSerializerTestCase(TestCase):
    """Test cases for StoryViewCreateSerializer"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            device_type=DeviceType.ANDROID,
            is_active=True
        )

        self.device = Device.objects.create(
            device_model='Samsung S21',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='device123',
            ip_address='192.168.1.1',
            app_version=self.app_version,
            user=self.user
        )

        self.story = Story.objects.create(
            title='Test Story',
            status=StoryStatus.PUBLISHED,
            is_active=True
        )

    def test_create_story_view(self):
        """Test creating story view"""
        data = {
            'story': self.story.id,
            'duration_watched': 3,
            'completed': False
        }

        serializer = StoryViewCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_create_view_with_inactive_story(self):
        """Test creating view with inactive story"""
        inactive_story = Story.objects.create(
            title='Inactive Story',
            status=StoryStatus.DRAFT,
            is_active=False
        )

        data = {'story': inactive_story.id}

        serializer = StoryViewCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('story', serializer.errors)

    def test_create_view_without_story(self):
        """Test creating view without story"""
        data = {
            'duration_watched': 3,
            'completed': True
        }

        serializer = StoryViewCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('story', serializer.errors)

    def test_create_view_with_optional_fields(self):
        """Test creating view with optional fields"""
        data = {'story': self.story.id}

        serializer = StoryViewCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())


class StoryPublicSerializerTestCase(TestCase):
    """Test cases for StoryPublicSerializer"""

    def setUp(self):
        """Set up test data"""
        self.story = Story.objects.create(
            title='Public Story',
            description='Public description',
            story_type=StoryType.PROMOTION,
            status=StoryStatus.PUBLISHED,
            is_active=True,
            duration=5,
            action_url='https://example.com'
        )

    def test_serializer_limited_fields(self):
        """Test serializer only exposes public fields"""
        serializer = StoryPublicSerializer(self.story)

        expected_fields = [
            'id', 'uuid', 'title', 'description',
            'story_type', 'duration', 'action_url',
            'is_featured', 'order'
        ]

        # These fields should be present
        for field in expected_fields:
            self.assertIn(field, serializer.data)

        # These fields should NOT be present (security)
        private_fields = ['view_count', 'click_count', 'created_at']
        for field in private_fields:
            self.assertNotIn(field, serializer.data)

    def test_serializer_multiple_public_stories(self):
        """Test serializing multiple public stories"""
        Story.objects.create(
            title='Story 2',
            story_type=StoryType.NEWS,
            status=StoryStatus.PUBLISHED,
            is_active=True
        )

        stories = Story.objects.filter(
            status=StoryStatus.PUBLISHED,
            is_active=True
        )

        serializer = StoryPublicSerializer(stories, many=True)

        self.assertEqual(len(serializer.data), 2)

        for story_data in serializer.data:
            self.assertIn('title', story_data)
            self.assertIn('story_type', story_data)
            self.assertNotIn('view_count', story_data)