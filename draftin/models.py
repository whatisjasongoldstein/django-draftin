from __future__ import absolute_import

import os
import lxml.html
import uuid
import datetime
import requests
import markdown
import hashlib
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from PIL import Image

from django.db import models
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ValidationError

from .settings import DRAFTIN_SETTINGS


def resize_image(path, size):
    """
    Limits image (path) to the dimensions passed as [w,h]
    """
    im = Image.open(path)
    if im.size[0] > size[0] or im.size[1] > size[1]:
        im.thumbnail(size, resample=Image.ANTIALIAS)
        im.save(path)


class Collection(models.Model):
    """
    Webhook for Draft, which can be attached to another
    kind of content like a site or a blog.
    """
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    parent = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=255, default="")
    uuid = models.CharField(max_length=255, editable=False)
    auto_publish = models.BooleanField(default=True)

    def __unicode__(self):
        if self.name:
            return self.name
        elif self.parent and self.uuid:
            return "%s (%s)" % (self.parent, self.uuid)
        return unicode(self.parent) or unicode(self.uuid) or u"New Collection" 

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        if not self.name:
            self.name = "Collection No. %s" % self.id
        return super(Collection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("draftin.endpoint", kwargs={"uuid": self.uuid})


class Draft(models.Model):
    """Article content provided by Draft."""

    collection = models.ForeignKey(Collection)
    draft_id = models.IntegerField(blank=True, null=True)
    external_url = models.URLField(blank=True, default="")
    name = models.CharField("Title", max_length=512)
    slug = models.CharField(max_length=255, default="", blank=True, unique=True)
    content = models.TextField(default="", blank=True)
    content_html = models.TextField(default="", blank=True)
    draftin_user_id = models.IntegerField(blank=True, null=True)
    draftin_user_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    date_published = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name or self.draft_id

    @cached_property
    def wordcount(self):
        return len(filter(None, self.content.split(" ")))

    def clean(self, *args, **kwargs):
        if not self.draft_id and not self.external_url:
            raise ValidationError("A Draft ID or External URL is required.")
        
        if self.external_url:
            self.download_content()
        return super(Draft, self).clean(*args, **kwargs)            

    def save(self, *args, **kwargs):
        # Ensure a unique slug
        if not self.slug:
            proposed_slug = slugify(self.name)
            if Draft.objects.filter(slug=proposed_slug).count():
                proposed_slug = "%s-%s" % (proposed_slug, uuid.uuid4())
            self.slug = proposed_slug[:255]
        
        # Set date published
        if self.published and not self.date_published:
            self.date_published = datetime.datetime.now()

        return super(Draft, self).save(*args, **kwargs)

    def download_content(self):
        url = self.external_url
        if url.startswith("https://www.dropbox.com"):
            url = url.replace("https://www.dropbox.com", "https://dl.dropbox.com", 1)
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            raise ValidationError("External url failed to scrape.")
        self.content = resp.text
        self.content_html = markdown.markdown(resp.text,
            extensions=['markdown.extensions.fenced_code', 'markdown.extensions.footnotes'])
        self.download_images()

    def download_images(self):
        tree = lxml.html.fragment_fromstring(self.content_html, create_parent="div")
        images = tree.xpath("//img[@src]")
        for img in images:
            src = img.attrib["src"]
            if src.startswith(settings.MEDIA_URL):
                continue  # Don't repeat

            try:
                resp = requests.get(src)
            except requests.exceptions.MissingSchema:
                continue

            filename = resp.headers.get("x-file-name")
            if not filename:  # Build from the src if its not in the header
                filename = "%s.jpg" % hashlib.md5(urlparse.urlparse(src).path).hexdigest()

            directory = os.path.join("draftin/img", str(self.id))
            
            file_path = os.path.join(settings.MEDIA_ROOT, directory, filename)
            file_url = os.path.join(settings.MEDIA_URL, directory, filename)

            # Update the content
            self.content = self.content.replace(src, file_url)
            img.attrib["src"] = file_url

            # If this item exists, skip it
            if os.path.exists(file_path):
                continue

            # Download the file
            directory = os.path.join(settings.MEDIA_ROOT, directory)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, "wb") as f:
                f.write(resp.content)
                f.close()

            # Resize image
            resize_image(file_path, DRAFTIN_SETTINGS["MAX_IMAGE_SIZE"])

        self.content_html = lxml.html.tostring(tree)
        self.save()

