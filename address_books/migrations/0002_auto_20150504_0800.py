# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address_books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='group',
            field=models.ForeignKey(related_name='addresses', to='address_books.Group'),
        ),
        migrations.RemoveField(
            model_name='addressbook',
            name='shared_with',
        ),
        migrations.AddField(
            model_name='addressbook',
            name='shared_with',
            field=models.ManyToManyField(related_name='shared_address_books_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
