from django.urls import path

from apps.contact.views import ContactListCreateAPIView, ContactRetrieveUpdateDestroyAPIView

app_name = 'contact'

urlpatterns = [
    path('', ContactListCreateAPIView.as_view(), name='contact-list-create'),
    path('<int:pk>/', ContactRetrieveUpdateDestroyAPIView.as_view(), name='contact-detail'),
]
