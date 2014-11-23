from django.conf.urls import patterns, url
from .views import endpoint

urlpatterns = patterns('',
    url(r'^(?P<uuid>[-\w\d]+)/$', endpoint, name="draftin.endpoint"),
)