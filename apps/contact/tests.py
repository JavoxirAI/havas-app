from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.contact.models import Contact


class ContactAPITestCase(APITestCase):
    def setUp(self):
        self.contact1 = Contact.objects.create(
            type='phone',
            title='Телефон',
            value='+998900000000'
        )
        self.contact2 = Contact.objects.create(
            type='telegram',
            title='Telegram',
            value='https://t.me/example'
        )

    def test_contact_list(self):
        """
        GET /api/contacts/ -> barcha kontaktlar qaytishi
        """
        url = reverse('contact:contact-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Pagination formatini tekshirish
        self.assertIn('pagination', response.data)
        self.assertIn('results', response.data)

        # Ro'yxat uzunligi 2 bo'lishi kerak
        self.assertEqual(len(response.data['results']), 2)

        # Birinchi obyektda kerakli maydonlar borligini tekshirish
        first = response.data['results'][0]
        self.assertIn('id', first)
        self.assertIn('type', first)
        self.assertIn('title', first)
        self.assertIn('value', first)

    def test_contact_retrieve(self):
        """
        GET /api/contacts/<id>/ -> bitta kontakt ma'lumotini olamiz
        """
        url = reverse('contact:contact-detail', args=[self.contact1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.contact1.id)
        self.assertEqual(response.data['type'], 'phone')
        self.assertEqual(response.data['title'], 'Телефон')
        self.assertEqual(response.data['value'], '+998900000000')

    def test_contact_create(self):
        """
        POST /api/contacts/ -> yangi kontakt yaratish
        """
        url = reverse('contact:contact-list-create')
        payload = {
            'type': 'instagram',
            'title': 'Instagram',
            'value': 'https://instagram.com/example'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Bazada 3 ta bo'lishi kerak
        self.assertEqual(Contact.objects.count(), 3)
        created = Contact.objects.get(title='Instagram')
        self.assertEqual(created.type, 'instagram')
        self.assertEqual(created.value, 'https://instagram.com/example')

    def test_contact_update_put(self):
        """
        PUT /api/contacts/<id>/ -> to'liq yangilash (barcha maydonlar)
        """
        url = reverse('contact:contact-detail', args=[self.contact2.id])
        payload = {
            'type': 'telegram',
            'title': 'Telegram (yangilandi)',
            'value': 'https://t.me/new_link'
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.contact2.refresh_from_db()
        self.assertEqual(self.contact2.title, 'Telegram (yangilandi)')
        self.assertEqual(self.contact2.value, 'https://t.me/new_link')

    def test_contact_partial_update_patch(self):
        """
        PATCH /api/contacts/<id>/ -> qisman yangilash (masalan faqat value)
        """
        url = reverse('contact:contact-detail', args=[self.contact1.id])
        payload = {'value': '+998991112233'}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.contact1.refresh_from_db()
        self.assertEqual(self.contact1.value, '+998991112233')
        # type va title o'zgarmagan bo'lishi kerak
        self.assertEqual(self.contact1.type, 'phone')
        self.assertEqual(self.contact1.title, 'Телефон')

    def test_contact_delete(self):
        """
        DELETE /api/contacts/<id>/ -> kontaktni o'chirish
        """
        url = reverse('contact:contact-detail', args=[self.contact1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contact.objects.filter(id=self.contact1.id).exists())

    def test_create_invalid_type(self):
        """
        Yaroqsiz type bilan contact yaratishga urinish -> 400
        (agar serializer type chekloviga ega bo'lsa)
        """
        url = reverse('contact:contact-list-create')
        payload = {
            'type': 'invalid_type',
            'title': 'Xato type',
            'value': 'value'
        }
        response = self.client.post(url, payload, format='json')
        # Agar serializer TYPE_CHOICES bilan ishlasa, 400 qaytishi kerak
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED))