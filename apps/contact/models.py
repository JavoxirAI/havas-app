from django.db import models


class Contact(models.Model):
    TYPE_CHOICES = [
        ('phone', 'Phone'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('gmail', 'Gmail'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=50)  # Masalan: Телефон
    value = models.CharField(max_length=255)  # Phone number yoki URL
    icon = models.ImageField(upload_to='contact_icons/', blank=True, null=True)

    def __str__(self):
        return self.title
