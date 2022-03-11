from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book.models import Book
from book.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.book1 = Book.objects.create(title='Book 1',
                                         price=122,
                                         author_name='Author 1')
        self.book2 = Book.objects.create(title='Book 2',
                                         price=222,
                                         author_name='Author 3')
        self.book3 = Book.objects.create(title='Book 3 Author 1',
                                         price=322,
                                         author_name='Author 2')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 122})
        serializer_data = BookSerializer([self.book1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BookSerializer([self.book1,
                                          self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BookSerializer([self.book3,
                                          self.book2,
                                          self.book1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)