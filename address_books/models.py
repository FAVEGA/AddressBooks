from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class AddressBook(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_address_books_set')
    shared_with = models.ManyToManyField(
        User, related_name='shared_address_books_set', blank=True
    )

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255)
    address_book = models.ForeignKey(AddressBook)

    def __str__(self):
        return str(self.address_book) + ' > ' + self.name


class Address(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    group = models.ForeignKey(Group, related_name='addresses')

    def __str__(self):
        return self.name + ' (' + self.email + ')'

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)