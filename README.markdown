A simple writing toolkit for Django. It can receive posts
from [Draftin](https://draftin.com/), scrape Markdown (from something
like Dropbox), or link to external posts on other blogs.

### Philosophy

1. A CMS is no place for writing. That's why so many writers copy
   paste from their tool of choice.
2. Markdown is pretty great.
3. There are many ways to put writing on the web. This one is mine.
   It doesn't need to aspire to be all things to all people, or
   to any people, for that matter.
4. When in doubt, inline content. Images are scraped. Gists are converted
   into fenced code blocks. 

### Basic Setup

1. Add `draftin` to installed apps
2. Something like:
   ```
   url(r'^draftin/webhooks/', include('draftin.urls')),
   ```
   in `urls.py`

### Extending Models

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

    def get_absolute_url(self):
        """
        The default model has no opinion on how it
        should appear on the front-end. The child model
        should decide.
        """
        return reverse(...)

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