# Generated by Django 4.0.3 on 2022-03-13 21:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('book', '0007_alter_book_readers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='readers',
            field=models.ManyToManyField(related_name='books', through='book.UserBookRelation', to=settings.AUTH_USER_MODEL),
        ),
    ]
