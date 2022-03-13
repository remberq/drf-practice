from django.template.defaulttags import url
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from book.views import BookViewSet, auth, UserBookRelationView

router = SimpleRouter()

router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = [
    path('auth/', auth),

]
urlpatterns += router.urls
