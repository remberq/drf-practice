from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F
from django.test import TestCase

from book.models import Book, UserBookRelation
from book.serializers import BookSerializer, UserBookRelationSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='Remberq',
            first_name='Andrey',
            last_name='Saw'
        )
        self.user2 = User.objects.create(
            username='Remberq2',
            first_name='Boris',
            last_name='Johnson'
        )

        self.book1 = Book.objects.create(title='Book 1',
                                         price=122,
                                         author_name='Author 1',
                                         owner=self.user)
        self.book2 = Book.objects.create(title='Book 2',
                                         price=222,
                                         author_name='Author 1',
                                         owner=self.user)
        self.book3 = Book.objects.create(title='Book 3',
                                         price=322,
                                         author_name='Author 2',
                                         owner=self.user)

        self.relation = UserBookRelation.objects.create(user_id=self.user.id,
                                                        book_id=self.book1.id,
                                                        like=True,
                                                        in_bookmarks=True,
                                                        rate=5)
        self.relation2 = UserBookRelation.objects.create(user_id=self.user.id,
                                                         book_id=self.book2.id,
                                                         like=True,
                                                         in_bookmarks=True)
        self.relation3 = UserBookRelation.objects.create(user_id=self.user2.id,
                                                         book_id=self.book1.id,
                                                         like=False,
                                                         rate=1)
        self.relation4 = UserBookRelation.objects.create(user_id=self.user2.id,
                                                         book_id=self.book2.id,
                                                         like=False,
                                                         rate=5)
        self.relation5 = UserBookRelation.objects.create(user_id=self.user2.id,
                                                         book_id=self.book3.id,
                                                         like=False,
                                                         rate=5)
        self.books = Book.objects.all().annotate(
            annotate_likes=Count(Case(When(
                userbookrelation__like=True,
                then=1))),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('id')

    def test_ok(self):
        def test_ok(self):
            user1 = User.objects.create(username='user1',
                                        first_name='Ivan', last_name='Petrov')
            user2 = User.objects.create(username='user2',
                                        first_name='Ivan', last_name='Sidorov')
            user3 = User.objects.create(username='user3',
                                        first_name='1', last_name='2')

            book_1 = Book.objects.create(title='Test book 1', price=25,
                                         author_name='Author 1', owner=user1)
            book_2 = Book.objects.create(title='Test book 2', price=55,
                                         author_name='Author 2')

            UserBookRelation.objects.create(user=user1, book=book_1, like=True,
                                            rate=5)
            UserBookRelation.objects.create(user=user2, book=book_1, like=True,
                                            rate=5)
            user_book_3 = UserBookRelation.objects.create(user=user3,
                                                          book=book_1,
                                                          like=True)
            user_book_3.rate = 4
            user_book_3.save()

            UserBookRelation.objects.create(user=user1, book=book_2, like=True,
                                            rate=3)
            UserBookRelation.objects.create(user=user2, book=book_2, like=True,
                                            rate=4)
            UserBookRelation.objects.create(user=user3, book=book_2, like=False)

            books = Book.objects.all().annotate(
                annotated_likes=Count(
                    Case(When(userbookrelation__like=True, then=1)))
            ).order_by('id')
            data = BookSerializer(books, many=True).data
            expected_data = [
                {
                    'id': book_1.id,
                    'title': 'Test book 1',
                    'price': '25.00',
                    'author_name': 'Author 1',
                    'annotated_likes': 3,
                    'rating': '4.67',
                    'owner_name': 'user1',
                    'readers': [
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Petrov'
                        },
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Sidorov'
                        },
                        {
                            'first_name': '1',
                            'last_name': '2'
                        },
                    ]
                },
                {
                    'id': book_2.id,
                    'title': 'Test book 2',
                    'price': '55.00',
                    'author_name': 'Author 2',
                    'annotated_likes': 2,
                    'rating': '3.50',
                    'owner_name': '',
                    'readers': [
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Petrov'
                        },
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Sidorov'
                        },
                        {
                            'first_name': '1',
                            'last_name': '2'
                        },
                    ]
                },
            ]
            self.assertEqual(expected_data, data)

    def test_relation_data(self):
        data = UserBookRelationSerializer([self.relation,
                                           self.relation2,
                                           self.relation3], many=True).data
        relation_data = [
            {
                'book': self.book1.id,
                'like': True,
                'in_bookmarks': True,
                'rate': 5
            },
            {
                'book': self.book2.id,
                'like': True,
                'in_bookmarks': True,
                'rate': None
            },
            {
                'book': self.book1.id,
                'like': False,
                'in_bookmarks': False,
                'rate': 1
            },
        ]
        self.assertEqual(relation_data, data)
