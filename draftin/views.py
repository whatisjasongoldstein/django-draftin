import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Collection, Draft

@csrf_exempt
def endpoint(request, uuid):
    """
    Expected payload:

    {   
    "id": your_document_id,
    "name": "The Name of your Document",
    "content": "The plain-text markdown of your document",
    "content_html": "Your document rendered as HTML",
    "user": {
        id: 1, 
        email: 'usersemail@example.com'
    },
    "created_at": "2013-05-23T14:11:54-05:00",
    "updated_at": "2013-05-23T14:11:58-05:00"
    }
    """
    collection = get_object_or_404(Collection, uuid=uuid)

    try:
        data = json.loads(request.POST.get("payload"))
    except Exception:
        return HttpResponseBadRequest("Something is wrong with your post.")

    try:
        parameters = dict(
            name = data["name"],
            content = data["content"],
            content_html = data["content_html"],
            draftin_user_id = data["user"]["id"],
            draftin_user_email = data["user"]["email"],
            created_at = data["created_at"],
            updated_at = data["updated_at"],
        )
        defaults = {"published": collection.auto_publish}
        defaults.update(parameters)
    except KeyError as e:
        return HttpResponseBadRequest("%s is required" % e.message)

    draft, created = Draft.objects.get_or_create(
        draft_id=data["id"],
        collection=collection,
        defaults=defaults)

    if not created:
        for key, value in parameters.items():
            setattr(draft, key, value)
        draft.save()

    return HttpResponse("Thanks!")

