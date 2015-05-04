# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='owned_address_books_set')),
                ('shared_with', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='shared_address_books_set')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address_book', models.ForeignKey(to='address_books.AddressBook')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='group',
            field=models.ForeignKey(to='address_books.Group'),
        ),
    ]
