# LUXHARI

Luxury visual-shopping Flask application, ready for Render.

## Render environment variables
Only these are required for the built-in admin login:

- `USER_NAME`
- `USER_PASSWORD`

Do not put GitHub `ghp_...` tokens into the application. Keep GitHub credentials in GitHub/Render's repository connection.

## Render commands
Build:
`pip install -r requirements.txt`

Start:
`gunicorn run:app`

## Admin
Open `/admin/` and sign in with the exact `USER_NAME` and `USER_PASSWORD` values configured in Render. Leading/trailing spaces and accidentally wrapped quote characters are safely trimmed.

## Starter catalogue
A new database is automatically seeded to at least 50 listings in each of the 7 public categories (350+ launch records total). Starter photography uses real Pexels-hosted photography and is intended to be replaced/edited from Authority before final commercial launch.

## Editing products
Authority lets the owner create, edit, replace images, feature, and archive catalogue items.

## Caching
The PWA caches public/static catalogue resources for faster repeat visits. Admin, checkout, order tracking, and other private/live routes are deliberately not cached.
