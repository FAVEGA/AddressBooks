from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token

from address_books.views import *


urlpatterns = [
    url(r'^whoami/', get_current_user, name='whoami'),
    url(r'^api-token-auth/', obtain_auth_token, name='tokenauth'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^addressbooks/$', AddressBookListView.as_view(), name='addressbooks'),
    url(r'^addressbooks/(?P<pk>\d+)', AddressBookDetailView.as_view(),
        name='addressbook'),
    url(r'^groups/$', GroupListView.as_view(), name='groups'),
    url(r'^groups/(?P<pk>\d+)', GroupDetailView.as_view(), name='groups'),
    url(r'^addresses/$', AddressListView.as_view(), name='addresses'),
    url(r'^addresses/(?P<pk>\d+)', AddressDetailView.as_view(),
        name='address'),
    url(r'users/$', UserListView.as_view(), name='users'),
    url(r'users/(?P<pk>\d+)', UserDetailView.as_view(), name='user'),
]
