import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from book.models import Book, UserBookRelation
from book.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='Andrey')
        self.user2 = User.objects.create(username='Andrey2')
        self.book1 = Book.objects.create(title='Book 1',
                                         price=122,
                                         author_name='Author 1',
                                         owner=self.user)
        self.book2 = Book.objects.create(title='Book 2',
                                         price=222,
                                         author_name='Author 3',
                                         owner=self.user)
        self.book3 = Book.objects.create(title='Book 3 Author 1',
                                         price=322,
                                         author_name='Author 2',
                                         owner=self.user)
        self.detail_url = reverse('book-detail', args=(self.book1.id,))

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book1, self.book2, self.book3],
                                         many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_item(self):
        url = reverse('book-detail', args=(self.book3.pk,))
        self.client.force_login(self.user)
        response = self.client.get(url)
        serializer_data = BookSerializer(self.book3).data
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

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        self.client.force_login(self.user)
        data = {
            "title": "Programming in Python 3",
            "price": 150,
            "author_name": "Mark Summerfield"
        }
        json_data = json.dumps(data)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        self.client.force_login(self.user)
        data = {
            "title": self.book1.title,
            "price": 575,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(self.detail_url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()  # <- refresh to update object in this test
        self.assertEqual(575, self.book1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        self.client.force_login(self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())

    def test_update_not_owner(self):
        user2 = User.objects.create(username='Boris')
        self.client.force_login(user2)
        data = {
            "title": self.book1.title,
            "price": 575,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(self.detail_url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(
            string='У вас недостаточно прав для выполнения данного действия.',
            code='permission_denied')}, response.data)

        self.book1.refresh_from_db()  # <- refresh to update object in this test
        self.assertEqual(122, self.book1.price)

    def test_update_not_owner_but_staff(self):
        user2 = User.objects.create(username='Boris',
                                    is_staff=True)
        self.client.force_login(user2)
        data = {
            "title": self.book1.title,
            "price": 575,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(self.detail_url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()  # <- refresh to update object in this test
        self.assertEqual(575, self.book1.price)


class UserBookRelationApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='Andrey')
        self.user2 = User.objects.create(username='Andrey2')
        self.book1 = Book.objects.create(title='Book 1',
                                         price=122,
                                         author_name='Author 1',
                                         owner=self.user)
        self.book2 = Book.objects.create(title='Book 2',
                                         price=222,
                                         author_name='Author 3',
                                         owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertTrue(relation.like)

        data2 = {
            "in_bookmarks": True,
        }
        json_data2 = json.dumps(data2)
        response = self.client.patch(url, data=json_data2,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)

        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            "rate": 4,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertTrue(relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            "rate": 7,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertEqual(relation.rate, None)