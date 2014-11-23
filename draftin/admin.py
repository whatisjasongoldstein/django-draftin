from django.contrib import admin

from .models import Draft, Collection

class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    list_display = ['uuid', 'parent', 'auto_publish', "drafts"]

    def drafts(self, instance=None):
        if instance:
            return instance.draft_set.count()
        return ""

class DraftAdmin(admin.ModelAdmin):
    model = Draft
    list_display = ["name", "collection", "created_at", "updated_at", "published",]
    list_filter = ["published", "collection"]
    ordering = ["-updated_at", ]


admin.site.register(Draft, DraftAdmin)
admin.site.register(Collection, CollectionAdmin)