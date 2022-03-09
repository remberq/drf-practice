from django.urls import path
from rest_framework.routers import SimpleRouter

from book.views import BookViewSet

router = SimpleRouter()

router.register(r'book', BookViewSet)

urlpatterns = [

]
urlpatterns += router.urls
