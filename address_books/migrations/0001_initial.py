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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(related_name='owned_address_books_set', to=settings.AUTH_USER_MODEL)),
                ('shared_with', models.ManyToManyField(related_name='shared_address_books_set', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_share_address_books', 'Can share address books'),),
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address_book', models.ForeignKey(related_name='groups', to='address_books.AddressBook')),
            ],
        ),
        migrations.CreateModel(
            name='PermissionDummy',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
            ],
            options={
                'permissions': (('can_assign_permissions', 'Can assign permissions'),),
            },
        ),
        migrations.AddField(
            model_name='address',
            name='groups',
            field=models.ManyToManyField(related_name='addresses', to='address_books.Group'),
        ),
    ]
