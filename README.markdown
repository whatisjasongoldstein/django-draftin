DraftIn integration for Django.

### Setup

1. Add `draftin` to installed apps
2. Something like:
   ```
   url(r'^draftin/webhooks/', include('draftin.urls')),
   ```
   in `urls.py`

