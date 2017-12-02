from django.urls import re_path
from .views import endpoint

urlpatterns = [
    re_path(r'^(?P<uuid>[-\w\d]+)/$', endpoint, name="draftin.endpoint"),
]