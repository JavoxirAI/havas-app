from rest_framework import serializers

from apps.contact.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = Contact
        fields = ['id', 'type', 'title', 'value', 'icon']
