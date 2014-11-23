import uuid
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Collection(models.Model):
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    parent = generic.GenericForeignKey('content_type', 'object_id')
    uuid = models.CharField(max_length=255, editable=False)
    auto_publish = models.BooleanField(default=True)

    def __unicode__(self):
        if self.parent and self.uuid:
            return "%s (%s)" % (self.parent, self.uuid)
        return unicode(self.parent) or unicode(self.uuid) or u"New Collection" 

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        return super(Collection, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        pass


class Draft(models.Model):
    collection = models.ForeignKey(Collection)
    draft_id = models.IntegerField()
    name = models.CharField(max_length=512)
    content = models.TextField()
    content_html = models.TextField()
    draftin_user_id = models.IntegerField(blank=True, null=True)
    draftin_user_email = models.EmailField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_synced_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
