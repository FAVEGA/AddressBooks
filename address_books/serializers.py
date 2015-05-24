from django.contrib.auth.models import User, Permission
from rest_framework import serializers
from rest_framework.fields import CharField, SerializerMethodField, BooleanField
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
    groups = PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )
    owner = PrimaryKeyRelatedField(queryset=User.objects.all())
    shared_with = PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

    def filter_groups(self, queryset):
        user = self.context['request'].user
        return (
            queryset.filter(addressbook__shared_with__id=user.id)
            | queryset.filter(addressbook__owner__id=user.id)
        )

    def validate_name(self, value):
        if AddressBook.objects.filter(name=value).exists():
            raise serializers.ValidationError("Duplicate address book name")
        return value

    def validate_groups(self, value):
        user = self.context['request'].user
        for group in value:
            if (user not in group.addressbook.shared_with.all()
                    and user != group.addressbook.owner):
                raise serializers.ValidationError("Invalid group set")
        return value

    def validate_shared_with(self, value):
        if not self.context['request'].user.has_perm('share_addressbook'):
            raise PermissionError(
                "You don't have permission to share address books"
            )
        return value

    class Meta:
        fields = ['id', 'name', 'groups', 'owner', 'shared_with']
        model = AddressBook


class GroupSerializer(FilterRelatedMixin, ModelSerializer):
    name = CharField()
    addressbook = PrimaryKeyRelatedField(queryset=AddressBook.objects.all())
    addresses = PrimaryKeyRelatedField(queryset=Address.objects.all(),
                                       many=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if Group.objects.filter(
                name=attrs['name'], addressbook=attrs['addressbook']
        ).exists():
            raise serializers.ValidationError("Duplicate group name")
        return attrs

    def validate_addressbook(self, value):
        user = self.context['request'].user
        if user not in value.shared_with.all() and user != value.owner:
            raise serializers.ValidationError("Invalid address book")
        return value

    def validate_addresses(self, value):
        user = self.context['request'].user
        for address in value:
            if (user not in address.group.addressbook.shared_with.all()
                    and user != address.group.addressbook.owner):
                raise serializers.ValidationError("Invalid addresses")
        return value

    def filter_addressbook(self, queryset):
        user = self.context['request'].user
        return queryset.filter(shared_with__id=user.id) | queryset.filter(
            owner__id=user.id)

    def filter_addresses(self, queryset):
        user = self.context['request'].user
        return (queryset.filter(groups__addressbook__shared_with__id=user.id)
                | queryset.filter(groups__addressbook__owner__id=user.id)) 

    class Meta:
        fields = ['id', 'name', 'addressbook', 'addresses']
        model = Group


class AddressSerializer(FilterRelatedMixin, ModelSerializer):
    name = CharField()
    email = CharField()
    groups = PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    def validate(self, data):
        # Check that the email is not a duplicate
        q = Address.objects.filter(
            email=data['email'], groups__addressbook__groups__in=data['groups']
        )
        q = q.exclude(id=self.instance.id) if self.instance is not None else q
        if q.exists():
            raise serializers.ValidationError("Duplicate email address")
        return data

    def validate_group(self, value):
        user = self.context['request'].user
        for group in value:
            if (user not in group.addressbook.shared_with.all()
                    and user != group.addressbook.owner):
                raise serializers.ValidationError("Invalid group set")
        return value

    def filter_group(self, queryset):
        user = self.context['request'].user
        return (queryset.filter(addressbook__shared_with__id=user.id)
                | queryset.filter(addressbook__owner__id=user.id))

    class Meta:
        fields = ['id', 'name', 'email', 'groups']
        model = Address


class PermissionField(serializers.Field):
    def __init__(self, *args, **kwargs):
        self.permission = kwargs.pop('permission')
        super().__init__(*args, source='*', **kwargs)

    def get_attribute(self, instance):
        perm = Permission.objects.get(
            codename=self.permission,
            content_type__app_label='addressbooks'
        )
        return perm in instance.user_permissions.all()

    def to_representation(self, data):
        return data

    def to_internal_value(self, data):
        return {self.permission: data.lower() == 'true'}


class UserSerializer(ModelSerializer):
    can_add_addressbook = PermissionField(permission='add_addressbook')
    can_change_addressbook = PermissionField(permission='change_addressbook')
    can_delete_addressbook = PermissionField(permission='delete_addressbook')
    can_share_addressbook = PermissionField(permission='share_addressbook')

    can_assign_permissions = PermissionField(permission='assign_permissions')

    can_add_group = PermissionField(permission='add_group')
    can_change_group = PermissionField(permission='change_group')
    can_delete_group = PermissionField(permission='delete_group')

    can_add_address = PermissionField(permission='add_address')
    can_change_address = PermissionField(permission='change_address')
    can_delete_address = PermissionField(permission='delete_address')

    def create(self, validated_data):
        permissions = dict()
        for field_name, field in self.fields.items():
            if isinstance(field, PermissionField):
                permissions[field.permission] = validated_data.pop(
                    field.permission
                )
                if permissions[field.permission] is not None:
                    raise PermissionError(
                        "You do not have permission to assign permissions"
                    )
        user = super().create(validated_data)
        for permission, value in permissions.items():
            permission = Permission.objects.get(
                codename=permission, content_type__app_label='addressbooks'
            )
            if value:
                user.user_permissions.add(permission)

        return user

    def update(self, instance, validated_data):
        permissions = dict()
        for field_name, field in self.fields.items():
            if isinstance(field, PermissionField):
                permissions[field.permission] = validated_data.pop(
                    field.permission
                )
        user = super().update(instance, validated_data)
        for permission, value in permissions.items():
            permission = Permission.objects.get(
                codename=permission, content_type__app_label='addressbooks'
            )
            if value:
                user.user_permissions.add(permission)
            else:
                user.user_permissions.remove(permission)

        return user

    class Meta:
        fields = ['id', 'username', 'email', 'can_add_addressbook',
                  'can_change_addressbook', 'can_delete_addressbook',
                  'can_add_group', 'can_change_group', 'can_delete_group',
                  'can_add_address', 'can_change_address', 'can_delete_address',
                  'can_assign_permissions', 'can_share_addressbook']
        model = User
