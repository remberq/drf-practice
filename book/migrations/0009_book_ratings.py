# Generated by Django 4.0.3 on 2022-03-14 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0008_alter_book_readers'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='ratings',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=3, null=True),
        ),
    ]
