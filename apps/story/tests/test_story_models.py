from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.story.models import Story, StoryView, StoryType, StoryStatus
from apps.users.models.user import User
from apps.users.models.device import Device, AppVersion, DeviceType


class StoryModelTestCase(TestCase):
    """Test cases for Story model"""

    def setUp(self):
        """Set up test data"""
        self.story_data = {
            'title': 'New Product Launch',
            'description': 'Check out our latest product!',
            'story_type': StoryType.PROMOTION,
            'status': StoryStatus.PUBLISHED,
            'order': 1,
            'duration': 5,
            'is_active': True,
        }

    def test_create_story_success(self):
        """Test creating a story successfully"""
        story = Story.objects.create(**self.story_data)

        self.assertEqual(story.title, 'New Product Launch')
        self.assertEqual(story.story_type, StoryType.PROMOTION)
        self.assertEqual(story.status, StoryStatus.PUBLISHED)
        self.assertEqual(story.duration, 5)
        self.assertTrue(story.is_active)

    def test_story_default_values(self):
        """Test story default values"""
        story = Story.objects.create(
            title='Test Story',
            description='Test description'
        )

        self.assertEqual(story.story_type, StoryType.ALL)
        self.assertEqual(story.status, StoryStatus.DRAFT)
        self.assertEqual(story.order, 0)
        self.assertEqual(story.duration, 5)
        self.assertTrue(story.is_active)
        self.assertFalse(story.is_featured)
        self.assertEqual(story.view_count, 0)
        self.assertEqual(story.click_count, 0)

    def test_story_types(self):
        """Test different story types"""
        story_types = [
            (StoryType.PROMOTION, 'Promotion'),
            (StoryType.NEWS, 'News'),
            (StoryType.ANNOUNCEMENT, 'Announcement'),
            (StoryType.FEATURED, 'Featured'),
            (StoryType.ALL, 'All'),
        ]

        for stype, label in story_types:
            story = Story.objects.create(
                title=f'Story {stype}',
                story_type=stype
            )

            self.assertEqual(story.story_type, stype)
            self.assertEqual(story.get_story_type_display(), label)

    def test_story_statuses(self):
        """Test different story statuses"""
        statuses = [
            (StoryStatus.DRAFT, 'Draft'),
            (StoryStatus.PUBLISHED, 'Published'),
            (StoryStatus.ARCHIVED, 'Archived'),
        ]

        for status_val, label in statuses:
            story = Story.objects.create(
                title=f'Story {status_val}',
                status=status_val
            )

            self.assertEqual(story.status, status_val)
            self.assertEqual(story.get_status_display(), label)

    def test_story_duration_validation(self):
        """Test story duration must be between 1-30"""
        # Valid durations
        for duration in [1, 5, 15, 30]:
            story = Story.objects.create(
                title=f'Story {duration}s',
                duration=duration
            )
            self.assertEqual(story.duration, duration)

    def test_story_is_expired_property(self):
        """Test is_expired property"""
        now = timezone.now()

        # Not expired (future expiration)
        future_story = Story.objects.create(
            title='Future Story',
            expires_at=now + timedelta(days=1)
        )
        self.assertFalse(future_story.is_expired)

        # Expired (past expiration)
        past_story = Story.objects.create(
            title='Past Story',
            expires_at=now - timedelta(days=1)
        )
        self.assertTrue(past_story.is_expired)

        # No expiration set
        no_expiry_story = Story.objects.create(
            title='No Expiry Story',
            expires_at=None
        )
        self.assertFalse(no_expiry_story.is_expired)

    def test_story_is_published_property(self):
        """Test is_published property"""
        now = timezone.now()

        # Published and active, not expired
        published_story = Story.objects.create(
            title='Published Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            expires_at=now + timedelta(days=1)
        )
        self.assertTrue(published_story.is_published)

        # Draft status
        draft_story = Story.objects.create(
            title='Draft Story',
            status=StoryStatus.DRAFT,
            is_active=True
        )
        self.assertFalse(draft_story.is_published)

        # Inactive
        inactive_story = Story.objects.create(
            title='Inactive Story',
            status=StoryStatus.PUBLISHED,
            is_active=False
        )
        self.assertFalse(inactive_story.is_published)

        # Expired
        expired_story = Story.objects.create(
            title='Expired Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            expires_at=now - timedelta(days=1)
        )
        self.assertFalse(expired_story.is_published)

    def test_story_increment_view_count(self):
        """Test incrementing view count"""
        story = Story.objects.create(**self.story_data)

        self.assertEqual(story.view_count, 0)

        story.increment_view_count()
        self.assertEqual(story.view_count, 1)

        story.increment_view_count()
        self.assertEqual(story.view_count, 2)

    def test_story_increment_click_count(self):
        """Test incrementing click count"""
        story = Story.objects.create(**self.story_data)

        self.assertEqual(story.click_count, 0)

        story.increment_click_count()
        self.assertEqual(story.click_count, 1)

        story.increment_click_count()
        self.assertEqual(story.click_count, 2)

    def test_get_active_stories(self):
        """Test getting active published stories"""
        now = timezone.now()

        # Active published story
        active = Story.objects.create(
            title='Active Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            order=1
        )

        # Draft story (shouldn't appear)
        Story.objects.create(
            title='Draft Story',
            status=StoryStatus.DRAFT,
            is_active=True
        )

        # Inactive story (shouldn't appear)
        Story.objects.create(
            title='Inactive Story',
            status=StoryStatus.PUBLISHED,
            is_active=False
        )

        # Expired story (shouldn't appear)
        Story.objects.create(
            title='Expired Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            expires_at=now - timedelta(days=1)
        )

        active_stories = Story.get_active_stories()

        self.assertEqual(active_stories.count(), 1)
        self.assertEqual(active_stories.first().id, active.id)

    def test_get_featured_stories(self):
        """Test getting featured stories"""
        # Featured story
        featured = Story.objects.create(
            title='Featured Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            is_featured=True
        )

        # Not featured
        Story.objects.create(
            title='Regular Story',
            status=StoryStatus.PUBLISHED,
            is_active=True,
            is_featured=False
        )

        featured_stories = Story.get_featured_stories()

        self.assertEqual(featured_stories.count(), 1)
        self.assertEqual(featured_stories.first().id, featured.id)

    def test_story_ordering(self):
        """Test story ordering by order field and published_at"""
        now = timezone.now()

        story1 = Story.objects.create(
            title='Story 1',
            order=2,
            published_at=now - timedelta(hours=1)
        )

        story2 = Story.objects.create(
            title='Story 2',
            order=1,
            published_at=now
        )

        story3 = Story.objects.create(
            title='Story 3',
            order=1,
            published_at=now - timedelta(hours=2)
        )

        stories = Story.objects.all()

        # Should be ordered by order ASC, then published_at DESC
        self.assertEqual(stories[0].id, story2.id)  # order=1, newest
        self.assertEqual(stories[1].id, story3.id)  # order=1, older
        self.assertEqual(stories[2].id, story1.id)  # order=2

    def test_story_string_representation(self):
        """Test __str__ method"""
        story = Story.objects.create(**self.story_data)

        expected = f"{story.title} ({story.get_story_type_display()})"
        self.assertEqual(str(story), expected)


class StoryViewModelTestCase(TestCase):
    """Test cases for StoryView model"""

    def setUp(self):
        """Set up test data"""
        self.story = Story.objects.create(
            title='Test Story',
            status=StoryStatus.PUBLISHED,
            is_active=True
        )

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

    def test_create_story_view(self):
        """Test creating a story view"""
        view = StoryView.objects.create(
            story=self.story,
            device=self.device,
            user=self.user,
            duration_watched=3,
            completed=False
        )

        self.assertEqual(view.story, self.story)
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.device, self.device)
        self.assertEqual(view.duration_watched, 3)
        self.assertFalse(view.completed)

    def test_story_view_default_values(self):
        """Test default values"""
        view = StoryView.objects.create(
            story=self.story,
            device=self.device
        )

        self.assertEqual(view.duration_watched, 0)
        self.assertFalse(view.completed)

    def test_story_view_unique_together(self):
        """Test unique_together constraint"""
        # Create first view
        StoryView.objects.create(
            story=self.story,
            device=self.device,
            user=self.user
        )

        # Try to create duplicate
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            StoryView.objects.create(
                story=self.story,
                device=self.device,
                user=self.user
            )

    def test_story_view_string_representation(self):
        """Test __str__ method"""
        view = StoryView.objects.create(
            story=self.story,
            user=self.user,
            device=self.device
        )

        expected = f"{self.user.username} viewed {self.story.title}"
        self.assertEqual(str(view), expected)

    def test_story_view_anonymous_user(self):
        """Test view without user (anonymous)"""
        view = StoryView.objects.create(
            story=self.story,
            device=self.device,
            user=None
        )

        self.assertIsNone(view.user)
        self.assertIn("Anonymous", str(view))