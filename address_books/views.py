from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from address_books.models import Group, AddressBook, Address
from address_books.serializers import AddressSerializer, AddressBookSerializer, \
    GroupSerializer


class AddressBookListView(generics.ListCreateAPIView):
    serializer_class = AddressBookSerializer

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return (AddressBook.objects.filter(owner=user)
                | AddressBook.objects.filter(shared_with__id=user.id))


class AddressBookDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressBookSerializer

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return (AddressBook.objects.filter(owner=user)
                | AddressBook.objects.filter(shared_with__id=user.id))


class GroupListView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Group.objects.filter(address_book__shared_with__id=user.id)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Group.objects.filter(address_book__shared_with__id=user.id)


class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Address.objects.filter(
            group__address_book__shared_with__id=user.id
        )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Address.objects.filter(
            group__address_book__shared_with__id=user.id
        )