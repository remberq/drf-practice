import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from book.models import Book, UserBookRelation
from book.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_username', )
        self.book_1 = Book.objects.create(title='Test book 1', price=25,
                                          author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(title='Test book 2', price=55,
                                          author_name='Author 5')
        self.book_3 = Book.objects.create(title='Test book Author 1', price=55,
                                          author_name='Author 2')

        UserBookRelation.objects.create(user=self.user, book=self.book_1,
                                        like=True,
                                        rate=5)

    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
            annotated_likes=Count(
                Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_item(self):
        books = Book.objects.filter(id=self.book_3.id).annotate(
            annotate_likes=Count(Case(When(userbookrelation__like=True,
                                           then=1))),

        ).order_by('id').first()

        url = reverse('book-detail', args=(self.book_3.pk,))
        self.client.force_login(self.user)
        response = self.client.get(url)
        serializer_data = BookSerializer(books).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(
            id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(
                Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        response = self.client.get(url, data={'price': 55})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(
            id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(
                Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        books = Book.objects.filter(
            id__in=[self.book_1.pk, self.book_2.id, self.book_3.id]).annotate(
            annotate_likes=Count(Case(When(userbookrelation__like=True,
                                           then=1))),

        ).order_by('-price')
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BookSerializer(books, many=True).data
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
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertEqual(3, Book.objects.all().count())
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2', )
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(
            string='У вас недостаточно прав для выполнения данного действия.',
            code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2',
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)


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
