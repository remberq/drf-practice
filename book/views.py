from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from book.models import Book
from book.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
