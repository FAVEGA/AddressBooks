from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from address_books.models import AddressBook, Group, Address
import json


class AddressBookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_token(self):
        """
        Ensure we can get the API token given an username and a password
        """
        url = reverse('tokenauth')
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], None)

    def test_get_addressbooks_no_data(self):
        url = reverse('addressbooks')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 0)

    def test_get_addressbooks(self):
        count = 100
        for x in range(count):
            AddressBook.objects.create(name=str(x), owner=self.user)
        url = reverse('addressbooks')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], count)

    def test_get_addressbook(self):
        id = AddressBook.objects.create(name='Test', owner=self.user).id
        url = reverse('addressbook', args=[id, ])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test')

    def test_add_addressbook(self):
        url = reverse('addressbooks')
        data = {'name': 'Test', 'owner': self.user.id}
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add address book',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_duplicate_addressbook(self):
        url = reverse('addressbooks')
        data = {'name': 'Test', 'owner': self.user.id}
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add address book',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_addressbook(self):
        id = AddressBook.objects.create(name='Test', owner=self.user).id
        url = reverse('addressbook', args=[id, ])
        data = {'name': 'Test1', 'owner': self.user.id}
        response = self.client.put(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can change address book',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.put(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test1')

    def test_delete_addressbook(self):
        id = AddressBook.objects.create(name='Test', owner=self.user).id
        url = reverse('addressbook', args=[id, ])
        response = self.client.delete(url)
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can delete address book',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.parent_addressbook_1 = AddressBook.objects.create(name="Test1",
                                                               owner=self.user)
        self.parent_addressbook_2 = AddressBook.objects.create(name="Test2",
                                                               owner=self.user)

    def test_get_groups_no_data(self):
        url = reverse('groups')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 0)

    def test_get_groups(self):
        count = 100
        for x in range(count):
            Group.objects.create(name=str(x),
                                 addressbook=self.parent_addressbook_1)
        url = reverse('groups')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], count)

    def test_get_group(self):
        id = Group.objects.create(name='Test',
                                  addressbook=self.parent_addressbook_1).id
        url = reverse('group', args=[id, ])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test')

    def test_add_group(self):
        url = reverse('groups')
        data = {'name': 'Test', 'addressbook': self.parent_addressbook_1.id}
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add group',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_duplicate_group(self):
        url = reverse('groups')
        data = {'name': 'Test', 'addressbook': self.parent_addressbook_1.id}
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add group',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'name': 'Test', 'addressbook': self.parent_addressbook_2.id}
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_update_group(self):
        id = Group.objects.create(name='Test',
                                  addressbook=self.parent_addressbook_1).id
        url = reverse('group', args=[id, ])
        data = {'name': 'Test1', 'addressbook': self.parent_addressbook_1.id}
        response = self.client.put(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can change group',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.put(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test1')

    def test_delete_group(self):
        id = Group.objects.create(name='Test',
                                  addressbook=self.parent_addressbook_1).id
        url = reverse('group', args=[id, ])
        response = self.client.delete(url)
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can delete group',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class AddressesTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.parent_addressbook_1 = AddressBook.objects.create(name="Test1",
                                                               owner=self.user)
        self.parent_addressbook_2 = AddressBook.objects.create(name="Test2",
                                                               owner=self.user)
        self.parent_group_1 = Group.objects.create(
            name='Group1',
            addressbook=self.parent_addressbook_1
        )
        self.parent_group_2 = Group.objects.create(
            name='Group2',
            addressbook=self.parent_addressbook_1
        )
        self.parent_addressbook_2_group = Group.objects.create(
            name='Group2',
            addressbook=self.parent_addressbook_2
        )

    def test_get_addresses_no_data(self):
        url = reverse('addresses')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 0)

    def test_get_addresses(self):
        count = 100
        for x in range(count):
            address = Address.objects.create(name=str(x), email=str(x))
            address.groups.add(self.parent_group_1)
            address.save()
        url = reverse('addresses')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], count)

    def test_get_addresses_by_group(self):
        count = 100
        for x in range(count):
            address = Address.objects.create(name=str(x), email=str(x))
            if x % 2:
                address.groups.add(self.parent_group_2)
            else:
                address.groups.add(self.parent_group_1)
            address.save()
        url = reverse('addresses') + '?group=' + str(self.parent_group_1.id)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], count/2)

    def test_get_address(self):
        address = Address.objects.create(name='Test', email='Test')
        address.groups.add(self.parent_group_1)
        address.save()
        id = address.id
        url = reverse('address', args=[id, ])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test')

    def test_add_address(self):
        url = reverse('addresses')
        data = {
            'name': 'Test', 'email': 'test@test.com',
            'groups': [self.parent_group_1.id, ]
        }
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add address',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_duplicate_address(self):
        url = reverse('addresses')
        data = {'name': 'Test', 'email': 'test@test.com',
                'groups': [self.parent_group_1.id, ]}
        response = self.client.post(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can add address',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'name': 'Test', 'email': 'test@test.com',
                'groups': [self.parent_addressbook_2_group.id, ]}
        response = self.client.post(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_update_address(self):
        address = Address.objects.create(name='Test', email='Test')
        address.groups.add(self.parent_group_1)
        address.save()
        id = address.id
        url = reverse('address', args=[id, ])
        data = {'name': 'Test1', 'email': 'test@test.com',
                'groups': [self.parent_group_1.id, ]}
        response = self.client.put(url, data, format='json')
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can change address',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.put(url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'], 'Test1')

    def test_delete_address(self):
        address = Address.objects.create(name='Test', email='Test')
        address.groups.add(self.parent_group_1)
        address.save()
        id = address.id
        url = reverse('address', args=[id, ])
        response = self.client.delete(url)
        # Expect a 403, we don't have permission.
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        permission = Permission.objects.get(
            name='Can delete address',
            content_type__app_label='address_books'
        )
        self.user.user_permissions.add(permission)
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)