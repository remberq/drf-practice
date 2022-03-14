from django.db.models import Count, Case, When, Avg, F
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import ModelViewSet, GenericViewSet

from book.models import Book, UserBookRelation
from book.permissions import IsOwnerOrStaffOrReadOnly
from book.serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotate_likes=Count(Case(When(
            userbookrelation__like=True,
            then=1))),
        owner_name=F('owner__username')
    ).prefetch_related('readers').order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['price']
    search_fields = ['author_name', 'title']
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(
            user=self.request.user,
            book_id=self.kwargs['book']  # <-- lookup_field
        )
        return obj


def auth(request):
    return render(request, 'book/index.html')
