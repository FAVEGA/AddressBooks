from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.authtoken.models import Token
from address_books.models import AddressBook, Group, Address
import json


class AddressBookTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'User 1', 'password')
        self.user2 = User.objects.create_user('user2', 'User 2', 'password')
        self.user3 = User.objects.create_user('user3', 'User 3', 'password')
        self.public_address_book = AddressBook.objects.create(
            name='Shared Address Book',
            owner=self.user1,
        )
        self.public_address_book.shared_with.add(self.user1, self.user2)

        self.user1_address_book = AddressBook.objects.create(
            name="User 1's Private Address Book",
            owner=self.user1,
        )
        self.user2_address_book = AddressBook.objects.create(
            name="User 2's Private Address Book",
            owner=self.user2,
        )

        self.user_1_address_book_group1 = Group.objects.create(
            name="User 1's Group 1",
            address_book=self.user1_address_book,
        )
        self.user_1_address_book_group2 = Group.objects.create(
            name="User 1's Group 2",
            address_book=self.user1_address_book,
        )

        self.user_1_address_book_group1_contact = Address.objects.create(
            name="User 1's Group 1 Address",
            email='dummy@tests.com',
            group=self.user_1_address_book_group1,
        )

    def test_login_token(self):
        response = self.client.post(
            reverse('tokenauth'), {'username': 'user1', 'password': 'password'})
        content = json.loads(response.content.decode('utf-8'))
        token = Token.objects.get(user=self.user1).key
        self.assertEquals(content['token'], token)
        response = self.client.get(reverse('groups'),
                                   HTTP_AUTHORIZATION='Token: ' + token)
        print(response.content)