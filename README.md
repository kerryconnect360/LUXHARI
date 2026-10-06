# LUXHARI — Luxury Visual Commerce Starter

A from-scratch Flask + HTML/CSS/JS storefront built for a visual, editorial shopping experience.

## Included

- Mobile-first luxury storefront with masonry discovery wall
- Clothing, Brands / Collections, Materials, On Model, Home & Living, Accessories, Inspiration
- Admin category visibility controls
- Product creation/editing/archive and image upload
- Brand logo upload and payment-information upload
- Cart and checkout
- Manual payment instructions with payment reference submission
- Order states: Pending, Payment initiated, Paid, Processing, Ready / Shipped, Completed, Cancelled
- Soft luxury post-payment receipt page
- Most Loved / heart interactions
- My Interests using browser storage
- Order tracking using order reference + phone
- PWA manifest + service worker
- SQLite locally; PostgreSQL-ready through DATABASE_URL
- Render deployment configuration

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
python run.py
```

Open http://127.0.0.1:5000/

Admin: http://127.0.0.1:5000/admin/login/

Set `USER_NAME` and `USER_PASSWORD` in `.env`.

## Payment

Admin → Settings lets you upload a “Where to Pay” image and edit the payment instructions. The checkout shows those instructions. Customers can enter a payment reference and submit it. For a true automated gateway later, the payment adapter can be attached to the existing checkout endpoint without redesigning the storefront.

## Production storage note

For Render, use a persistent PostgreSQL database via `DATABASE_URL`. Uploaded media is deliberately isolated in `uploads/` so it can later be switched to durable object storage (S3-compatible, Cloudinary, etc.) without changing product/order models.
