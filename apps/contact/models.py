from django.db import models


class Contact(models.Model):
    TYPE_CHOICES = [
        ('phone', 'Phone'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']  # ✅ Pagination warning ni hal qilish
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f"{self.title} ({self.type})"