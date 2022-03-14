from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from book.models import Book, UserBookRelation


class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BookSerializer(ModelSerializer):
    annotate_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    owner_name = serializers.CharField(
        read_only=True
    )
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'price',
            'author_name',
            'annotate_likes',
            'rating',
            'owner_name',
            'readers'
        )


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'rate', 'in_bookmarks')
