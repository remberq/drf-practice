from django.db import models


class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=7, decimal_places=2)

    def __str__(self):
        return self.title
