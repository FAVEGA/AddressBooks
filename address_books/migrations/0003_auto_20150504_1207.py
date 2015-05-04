# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('address_books', '0002_auto_20150504_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressbook',
            name='shared_with',
            field=models.ManyToManyField(related_name='shared_address_books_set', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
