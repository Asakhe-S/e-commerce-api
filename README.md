# yt-ecommerce-api

A simple Django REST API for products, categories and cart functionality — built from a YouTube tutorial.

## Overview

This repository contains a minimal e-commerce backend built with Django and Django REST Framework. It exposes endpoints for:

- Listing featured products
- Product detail by slug
- Listing categories and category detail
- Adding items to a cart and updating cart item quantity

## Quickstart (Windows / PowerShell)

1. Create and activate virtual environment (if not included):

```powershell
python -m venv ecommerceEnv
.\ecommerceEnv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run migrations and start the server:

```powershell
python manage.py migrate
python manage.py runserver
```

3. Use Postman or curl to hit endpoints (examples):

- `GET /product_list/`
- `GET /products/<slug>/`
- `POST /add_to_cart/` with JSON `{ "cart_code": "abc", "product_id": 1 }`
- `PUT /update_cartitem_quantity/` with JSON `{ "cart_item_id": 1, "quantity": 2 }`

## Notes

- Database used in this project: `db.sqlite3` (included in repo). If you prefer, remove it and re-run migrations.
- Update `ecommerceApiProject/settings.py` to configure production settings and `ALLOWED_HOSTS` before deploying.

## Suggested repository name & description

- **Repository name:** `yt-ecommerce-api`
- **Short description:** "A simple Django REST API for products, categories and cart functionality — built from a YouTube tutorial."

---

If you'd like, I can also add a `requirements.txt`, create a GitHub repo and push the code — I will need either your confirmation to push to `https://github.com/Asakhe-S/yt-ecommerce-api` (create an empty repo there first), or a GitHub personal access token so I can create the repository and push on your behalf.
