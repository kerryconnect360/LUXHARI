# LUXHARI — from-scratch Flask storefront

A mobile-first visual shopping storefront with an Authority admin area.

## Render — simplest setup

Environment variables:

- `USER_NAME`
- `USER_PASSWORD`

Nothing else is required for a first deployment. The Flask session key is derived from these two values, so you do not need to add a separate `SECRET_KEY` variable.

Start command:

`gunicorn run:app`

Build command:

`pip install -r requirements.txt`

## Starter catalogue

On an empty or nearly empty database, LUXHARI automatically ensures at least **50 records in each of the 7 public categories**. That means a launch-ready catalogue of at least 350 records. The starter entries use real Pexels photography as replaceable launch imagery; names, prices and stock are placeholders until the owner edits them in Authority.

The storefront paginates the catalogue at 48 items per page to keep first-load performance sensible.

Starter photography is used under the Pexels license. The imagery is presentation material, not a claim that pictured people or brands endorse LUXHARI. Replace starter images with LUXHARI-owned photography before treating the catalogue as final brand inventory.

## Authority

Open `/admin/` and sign in with `USER_NAME` and `USER_PASSWORD` from Render. The login accepts the exact values and is also tolerant of accidental surrounding whitespace. A compatibility fallback accepts legacy `USERNAME` / `PASSWORD` values if they exist, but `USER_NAME` / `USER_PASSWORD` are the intended variables.

Authority lets you create/edit/archive products, upload replacement images, upload the LUXHARI logo, configure contact details, configure "Where to Pay", and manage order/payment states.

## Payments / receipts

Checkout shows the owner-provided payment instructions and payment image. Customers can submit a payment reference and are then taken to a polished LUXHARI receipt page. Admins can move payment state through Pending → Payment initiated → Paid, and order state through the fulfilment lifecycle.

## PWA / caching

The service worker caches the application shell and previously viewed catalogue images. The application is designed to remain useful during temporary network drops, while the database remains the source of truth.
