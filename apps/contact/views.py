from rest_framework import generics
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from .models import Contact
from .serializers.serializers import ContactSerializer


class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = CustomPageNumberPagination


class ContactRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer