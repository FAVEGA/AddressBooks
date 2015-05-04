from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField, \
    RelatedField
from rest_framework.serializers import ModelSerializer

from address_books.models import AddressBook, Group, Address


class FilterRelatedMixin(object):
    """
    Used to filter related objects. Gets queryset from method named
    filter_{field_name}
    """

    def __init__(self, *args, **kwargs):
        super(FilterRelatedMixin, self).__init__(*args, **kwargs)
        for name in self.fields:
            field = self.fields[name]
            if isinstance(field, ManyRelatedField):
                field = field.child_relation
            if isinstance(field, RelatedField):
                method_name = 'filter_%s' % name
                try:
                    func = getattr(self, method_name)
                except AttributeError:
                    pass
                else:
                    field.queryset = func(field.queryset)


class AddressBookSerializer(FilterRelatedMixin, ModelSerializer):
    name = CharField()
    group_set = PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    def filter_group_set(self, queryset):
        user = self.context['request'].user
        return (
            queryset.filter(address_book__shared_with__id=user.id)
            | queryset.filter(address_book__owner__id=user.id)
        )

    def validate_group_set(self, value):
        user = self.context['request'].user
        for group in value:
            if (user not in group.address_book.shared_with
                    or user != group.address_book.owner):
                raise serializers.ValidationError("Invalid group set")
        return value

    class Meta:
        fields = ['id', 'name', 'group_set']
        model = AddressBook


class GroupSerializer(FilterRelatedMixin, ModelSerializer):
    name = CharField()
    address_book = PrimaryKeyRelatedField(queryset=AddressBook.objects.all())
    addresses = PrimaryKeyRelatedField(queryset=Address.objects.all(),
                                       many=True)

    def __init__(self, *args, **kwargs):
        print(args, kwargs)
        super().__init__(*args, **kwargs)

    def validate_address_book(self, value):
        user = self.context['request'].user
        if user not in value.shared_with or user != value.owner:
            raise serializers.ValidationError("Invalid address book")
        return value

    def validate_addresses(self, value):
        user = self.context['request'].user
        for address in value:
            if (user not in address.group.address_book.shared_with
                    or user != address.group.address_book.owner):
                raise serializers.ValidationError("Invalid addresses")
        return value

    def filter_address_book(self, queryset):
        user = self.context['request'].user
        return queryset.filter(shared_with__id=user.id) | queryset.filter(
            owner__id=user.id)

    def filter_addresses(self, queryset):
        user = self.context['request'].user
        return (queryset.filter(group__address_book__shared_with__id=user.id)
                | queryset.filter(group__address_book__owner__id=user.id))

    class Meta:
        fields = ['id', 'name', 'address_book', 'addresses']
        model = Address


class AddressSerializer(FilterRelatedMixin, ModelSerializer):
    name = CharField()
    email = CharField()
    group = PrimaryKeyRelatedField(queryset=Group.objects.all())

    def validate_group(self, value):
        user = self.context['request'].user
        if (user not in value.address_book.shared_with
                or user != value.address_book.owner):
            raise serializers.ValidationError("Invalid group set")
        return value

    def filter_group(self, queryset):
        user = self.context['request'].user
        return (queryset.filter(address_book__shared_with__id=user.id)
                | queryset.filter(address_book__owner__id=user.id))

    class Meta:
        fields = ['id', 'name', 'email', 'group']
        model = Group