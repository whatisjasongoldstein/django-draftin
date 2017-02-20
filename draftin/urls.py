from django.conf.urls import url
from .views import endpoint

urlpatterns = [
    url(r'^(?P<uuid>[-\w\d]+)/$', endpoint, name="draftin.endpoint"),
]