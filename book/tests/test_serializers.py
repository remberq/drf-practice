from django.test import TestCase

from book.models import Book
from book.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(title='Book 1', price=122)
        book2 = Book.objects.create(title='Book 2', price=222)
        book3 = Book.objects.create(title='Book 3', price=322)
        data = BookSerializer([book1, book2, book3], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'title': 'Book 1',
                'price': '122.00'
            },
            {
                'id': book2.id,
                'title': 'Book 2',
                'price': '222.00'
            },
            {
                'id': book3.id,
                'title': 'Book 3',
                'price': '322.00'
            }
        ]
        self.assertEqual(expected_data, data)
