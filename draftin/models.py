import uuid
import datetime
from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

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
    draft_id = models.IntegerField()
    name = models.CharField(max_length=512)
    slug = models.CharField(max_length=255, default="", blank=True, unique=True)
    content = models.TextField()
    content_html = models.TextField()
    draftin_user_id = models.IntegerField(blank=True, null=True)
    draftin_user_email = models.EmailField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_synced_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    date_published = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name or self.draft_id

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


