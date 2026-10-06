# LUXHARI

Luxury fashion + textile storefront built from scratch with Flask.

## Render — simple setup

Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn run:app`

Only set these Environment Variables for the basic deployment:

- `USER_NAME` — your Authority/admin username
- `USER_PASSWORD` — your Authority/admin password

No `SECRET_KEY` variable is required. The app creates a runtime session key automatically when one is not supplied.

No `DATABASE_URL` variable is required for the simple version. The app uses its local SQLite database when no database URL is supplied.

## Caching

LUXHARI includes a service worker that caches the app shell and previously fetched GET resources for faster repeat visits and basic offline access. Uploaded media is also returned with long browser-cache headers.

Browser caching is for speed/offline use; it is not a guarantee that Render's local filesystem or SQLite data survives a service restart or redeploy.

## GitHub / Render

Keep the repository connected through Render's GitHub integration. Do not place a GitHub `ghp_...` personal access token inside this application or commit one into the repository.
