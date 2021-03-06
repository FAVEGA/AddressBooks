from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
        return AddressBook.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()


class AddressBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressBookSerializer

    model = AddressBook

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return AddressBook.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()


class GroupListView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer

    model = Group

    authentication_classes = (
        SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        queryset = Group.objects.filter(
            (Q(addressbook__owner=user)
             | Q(addressbook__shared_with=user))
        ).distinct()
        addressbook = self.request.QUERY_PARAMS.get('addressbook', None)
        if addressbook is not None:
            queryset = queryset.filter(addressbook=addressbook)
        return queryset


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer

    model = Group

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Group.objects.filter(
            Q(addressbook__owner=user) | Q(addressbook__shared_with=user)
        ).distinct()


class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    model = Address

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        queryset = Address.objects.filter(
            (Q(groups__addressbook__owner=user)
             | Q(groups__addressbook__shared_with=user))
        ).distinct()
        group = self.request.QUERY_PARAMS.get('group', None)
        if group is not None:
            queryset = queryset.filter(groups__id=group)
        return queryset


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    model = Address

    authentication_classes = (SessionAuthentication, BasicAuthentication,
                              TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        return Address.objects.filter(
            (Q(groups__addressbook__owner=user)
             | Q(groups__addressbook__shared_with=user))
        ).distinct()


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


@api_view(['GET'])
def get_current_user(request):
    print('Reached get_current_user')
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
