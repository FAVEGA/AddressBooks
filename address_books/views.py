from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from address_books.models import Group, AddressBook, Address
from address_books.serializers import AddressSerializer, AddressBookSerializer, \
    GroupSerializer, UserSerializer


class AddressBookListView(generics.ListCreateAPIView):
    serializer_class = AddressBookSerializer

    model = AddressBook

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return (AddressBook.objects.filter(owner=user)
                | AddressBook.objects.filter(shared_with__id=user.id))


class AddressBookDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressBookSerializer

    model = AddressBook

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return (AddressBook.objects.filter(owner=user)
                | AddressBook.objects.filter(shared_with__id=user.id))


class GroupListView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer

    model = Group

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Group.objects.filter(address_book__shared_with__id=user.id)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer

    model = Group

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Group.objects.filter(address_book__shared_with__id=user.id)


class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    model = Address

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Address.objects.filter(
            groups__address_book__shared_with__id=user.id
        )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    model = Address

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Address.objects.filter(
            groups__address_book__shared_with__id=user.id
        )


class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    queryset = User.objects.all()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()

