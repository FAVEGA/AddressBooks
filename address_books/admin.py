from django.contrib import admin
from address_books.models import Group, Address, AddressBook


class AddressAdmin(admin.ModelAdmin):
    fields = ['name', 'email', 'groups']


class GroupAdmin(admin.ModelAdmin):
    fields = ['name', 'address_book', 'addresses']


class AddressBookAdmin(admin.ModelAdmin):
    fields = ['name', 'owner', 'shared_with']

admin.site.register(Address, AddressAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(AddressBook, AddressBookAdmin)