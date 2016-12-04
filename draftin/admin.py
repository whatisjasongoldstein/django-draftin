from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import Draft, Collection, Publication


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name','uuid', 'parent', 'auto_publish', "drafts", "webhook"]

    def drafts(self, instance=None):
        if instance:
            return instance.draft_set.count()
        return ""

    def webhook(self, instance=None):
        if instance:
            return '<a href="%s">Webhook</a>' % instance.get_absolute_url()
        return ""
    webhook.allow_tags = True


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    model = Publication


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    model = Draft
    list_display = ["name", "origin", "collection", 
        "created_at", "updated_at", "published",]
    list_filter = ["published", "collection"]
    ordering = ["-updated_at", ]
    readonly_fields = ["content", "content_html", 
        "draftin_user_id", "draftin_user_email", "origin"]
    fieldsets = (
        ("Metadata", {
            "fields": ("name", "slug",
                "description",
                "collection",
                ("date_published", "published", ),
            ),
        }),

        ("Source", {
            "fields": ("origin", "external_url", "publication", "canonical_url", )
        }),

        ("Content (Debug)", {
            "fields": ("content", "content_html", ),
            'classes': ('collapse',),
        }),
    )

    def origin(self, instance):
        if instance.draft_id:
            return "Draftin"
        elif instance.external_url and instance.publication:
            return "External Link"
        elif instance.external_url:
            return "Markdown scrape"
        return "Unknown"

    def save_model(self, request, obj, form, change):
        if not obj.draftin_user_email:
            obj.draftin_user_email = request.user.email
        super(DraftAdmin, self).save_model(request, obj, form, change)
