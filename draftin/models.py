from __future__ import absolute_import, unicode_literals

import re
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
from django.urls.exceptions import NoReverseMatch
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible

from .helpers import gist_to_markdown, dropbox_url
from .settings import DRAFTIN_SETTINGS


GIST_RE = re.compile(r'\<script src="https:\/\/gist\.github.com\/[\w]+\/([\w]+)\.js"\>\<\/script\>',
re.UNICODE)


def resize_image(path, size):
    """
    Limits image (path) to the dimensions passed as [w,h]
    """
    try:
        im = Image.open(path)
    except Exception:
        return

    if im.size[0] > size[0] or im.size[1] > size[1]:
        im.thumbnail(size, resample=Image.ANTIALIAS)
        im.save(path)


@python_2_unicode_compatible
class Collection(models.Model):
    """
    Webhook for Draft, which can be attached to another
    kind of content like a site or a blog.
    """
    content_type = models.ForeignKey(ContentType, blank=True, null=True,
        on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    parent = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=255, default="")
    uuid = models.CharField(max_length=255, editable=False)
    auto_publish = models.BooleanField(default=True)

    def __str__(self):
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
        try:
            return reverse("draftin.endpoint",
                kwargs={"uuid": self.uuid})
        except NoReverseMatch:
            pass


@python_2_unicode_compatible
class Publication(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, default="", blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Publication, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Draft(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    draft_id = models.IntegerField(blank=True, null=True, editable=False)
    external_url = models.URLField(blank=True, default="")
    publication = models.ForeignKey(Publication, blank=True, null=True,
        verbose_name="External Publication", on_delete=models.SET_NULL)
    canonical_url = models.URLField(blank=True, default="")
    name = models.CharField("Title", max_length=512)
    description = models.TextField(blank=True, default="", help_text="Optional dek.")
    image = models.ImageField(upload_to="draftin/img/%Y/%m/", blank=True, default="")
    slug = models.CharField(max_length=255, default="", blank=True, unique=True)
    content = models.TextField(default="", blank=True)
    content_html = models.TextField(default="", blank=True)
    draftin_user_id = models.IntegerField(blank=True, null=True)
    draftin_user_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    date_published = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name or self.draft_id

    @cached_property
    def wordcount(self):
        text = strip_tags(self.content_html) or self.content
        return len(list(filter(None, text.split(" "))))

    @cached_property
    def domain(self):
        url = self.canonical_url or self.external_url
        if url:
            return urlparse.urlparse(url).netloc
        return None

    def clean(self, *args, **kwargs):
        if not self.draft_id and not self.external_url:
            raise ValidationError("A Draft ID or External URL is required.")

        if self.external_url:
            self.download_content()
        return super(Draft, self).clean(*args, **kwargs)            

    def save(self, *args, **kwargs):
        # Ensure a unique slug
        if not self.slug:
            proposed_slug = slugify(self.name)[:255]
            if Draft.objects.filter(slug=proposed_slug).count():
                proposed_slug = "%s-%s" % (proposed_slug, uuid.uuid4())
            self.slug = proposed_slug
        
        # Set date published
        if self.published and not self.date_published:
            self.date_published = datetime.datetime.now()

        return super(Draft, self).save(*args, **kwargs)

    def download_content(self):

        # Scrape markdown files from Dropbox
        url = dropbox_url(self.external_url)
        if url.startswith("https://www.dropbox.com"):
            url = url.replace("https://www.dropbox.com", "https://dl.dropbox.com", 1)
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            raise ValidationError("External url failed to scrape.")
        self.content = resp.text

        # If any code is embedded as a gist, download those
        self.download_gists()

        # Make html
        self.content_html = markdown.markdown(self.content,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.footnotes',
            ])

        # Scrape images
        self.download_images()

    def download_images(self):
        tree = lxml.html.fragment_fromstring(self.content_html, create_parent="div")
        images = tree.xpath("//img[@src]")
        for img in images:
            src = dropbox_url(img.attrib["src"])
            if src.startswith(settings.MEDIA_URL):
                continue  # Don't repeat

            try:
                resp = requests.get(src)
            except requests.exceptions.MissingSchema:
                continue

            filename = resp.headers.get("x-file-name")
            if not filename:  # Build from the src if its not in the header
                filename = "%s.jpg" % hashlib.md5(urlparse.urlparse(src).path.encode("utf-8")).hexdigest()

            directory = os.path.join("draftin/img", str(self.id))
            
            file_path = os.path.join(settings.MEDIA_ROOT, directory, filename)
            file_url = os.path.join(settings.MEDIA_URL, directory, filename)

            # Update the content
            self.content = self.content.replace(src, file_url)
            img.attrib["src"] = file_url

            # If this item exists, skip it
            if os.path.exists(file_path) and os.path.getsize(file_path):
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

        self.content_html = lxml.html.tostring(tree, encoding="unicode")

    def download_gists(self):
        """
        If the post contains embedded gists, convert
        them to markdown fenced code and contain them
        in the contents.
        """
        matches = re.finditer(GIST_RE, self.content)
        for match in matches:
            md_gist = gist_to_markdown(match.groups()[0])
            if md_gist:
                self.content = self.content.replace(match.group(), md_gist)

