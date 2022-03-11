from django.test import TestCase

from book.models import Book
from book.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.book1 = Book.objects.create(title='Book 1',
                                         price=122,
                                         author_name='Author 1')
        self.book2 = Book.objects.create(title='Book 2',
                                         price=222,
                                         author_name='Author 1')
        self.book3 = Book.objects.create(title='Book 3',
                                         price=322,
                                         author_name='Author 2')

    def test_ok(self):
        data = BookSerializer([self.book1, self.book2, self.book3],
                              many=True).data
        expected_data = [
            {
                'id': self.book1.id,
                'title': 'Book 1',
                'price': '122.00',
                'author_name': 'Author 1'
            },
            {
                'id': self.book2.id,
                'title': 'Book 2',
                'price': '222.00',
                'author_name': 'Author 1'
            },
            {
                'id': self.book3.id,
                'title': 'Book 3',
                'price': '322.00',
                'author_name': 'Author 2'
            }
        ]
        self.assertEqual(expected_data, data)
