DraftIn integration for Django.

### Basic Setup

1. Add `draftin` to installed apps
2. Something like:
   ```
   url(r'^draftin/webhooks/', include('draftin.urls')),
   ```
   in `urls.py`


### Extending

I want to keep this lean, but most article apps will need images
and metadata. On [Be The Shoe](http://betheshoe.com), I do something
like this:

```python
from django.db import models
from draftin.models import Draft

class Post(models.Model):
    """
    All the metadata etc associated with the writing.
    """
    draft = models.OneToOneField(Draft, editable=False)
    title = models.CharField(...)
    author = models.ForeignKey(...)
    image = models.ImageField(...)


def create_posts_with_drafts(**kwargs):
    """
    Create a post any time a Draft is received.
    Using a signal let's me keep the site-specific
    logic decoupled.
    """
    obj = kwargs.get("instance", None)
    Post.objects.get_or_create(draft=obj, defaults={
        "title": obj.name,
        "slug": slugify(obj.name),
    })

models.signals.post_save.connect(create_posts_with_drafts, sender=Draft)

```

```python

from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
    model = Post
    readonly_fields = ["draft", "preview"]

    def preview(self, instance=None):
        if instance and instance.draft:
            return instance.draft.content_html
        return ""
    preview.allow_tags = True

admin.site.register(Post, PostAdmin)

```