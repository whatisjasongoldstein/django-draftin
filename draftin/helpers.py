import json
import requests

GIST_TEMPALTE = """
```%(language)s
%(content)s
```
"""

def gist_to_markdown(gist_id):
    """
    Get markdown fenced code from an embedded gist.
    """
    api_resp = requests.get("https://api.github.com/gists/%s" % gist_id)
    try:
        api_resp.raise_for_status()
    except Exception:
        return None
    data = json.loads(api_resp.content.decode("utf-8"))
    markdown_reps = []
    for f in data["files"].values():
        md = GIST_TEMPALTE % {
            "language": f["language"].lower(),
            "content": f["content"],
        }
        markdown_reps.append(md)
    return "\n\n".join(markdown_reps)