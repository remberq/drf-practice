from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book.models import Book
from book.serializers import BookSerializer


class BookApiTestCase(APITestCase):

    def test_get(self):
        book1 = Book.objects.create(title='Book 1', price=122)
        book2 = Book.objects.create(title='Book 2', price=222)
        book3 = Book.objects.create(title='Book 3', price=322)
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([book1, book2, book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
