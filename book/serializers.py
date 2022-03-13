from rest_framework.serializers import ModelSerializer

from book.models import Book, UserBookRelation


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        exclude = ['readers']


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'rate', 'in_bookmarks')
