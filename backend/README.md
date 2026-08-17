# ZAYNOR Backend

The FastAPI backend for the ZAYNOR e-commerce platform. Currently at **Phase 12** — coupon and discount code system is live.

## What Is This?

A Python backend server that powers the ZAYNOR website. It has JWT authentication, an admin dashboard, order tracking, product search, product reviews, email notifications, database migrations, rate limiting, a product wishlist, and a coupon/discount system.

## Setup (Windows)

### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv
```

### 2. Activate the virtual environment

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env
```

### 5. Seed the database

```bash
python -m app.seed
```

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

### 7. Open the frontend

- **Public site:** Open `index.html`
- **Admin dashboard:** Open `admin.html` — login with `admin@zaynor.com` / `admin123`
- **Track order:** Open `tracking.html`
- **Search:** Use the search bar or open `search.html?q=term`
- **Wishlist:** Open `wishlist.html`

## Coupon / Discount System

Admins can create discount codes. Customers apply them in the product modal — the discounted price shows inline and the coupon code is included in the WhatsApp order message.

### How It Works

1. **Admin creates a coupon** via `POST /api/v1/coupons/` (e.g. `WINTER20` for 20% off)
2. **Customer opens a product modal** → sees a coupon input field
3. **Customer enters code** → `POST /api/v1/coupons/validate` checks validity
4. **If valid** → price updates with strikethrough + discounted price, WhatsApp link includes the coupon
5. **Admin manages coupons** — list, create, update, delete via admin-only endpoints

### Coupon Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/coupons/validate` | No | Validate a coupon against an order amount |
| GET | `/api/v1/coupons/` | Admin | List all coupons |
| POST | `/api/v1/coupons/` | Admin | Create a new coupon |
| PUT | `/api/v1/coupons/{id}` | Admin | Update a coupon |
| DELETE | `/api/v1/coupons/{id}` | Admin | Delete a coupon |

### Coupon Properties

| Field | Description |
|-------|-------------|
| `code` | Unique uppercase code (e.g. `WELCOME10`) |
| `discount_percent` | Percentage off (1-100) |
| `min_order_amount` | Minimum order value to use the coupon |
| `max_uses` | Total usage limit (null = unlimited) |
| `is_active` | Enable/disable the coupon |
| `expires_at` | Expiration date (null = never expires) |

## Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Production Deployment

```bash
# Docker
docker build -t zaynor-backend .
docker run -d --name zaynor-api -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/zaynor \
  -e SECRET_KEY=your-production-secret-key \
  zaynor-backend

# Systemd
sudo systemctl enable zaynor
sudo systemctl start zaynor
```

## Available Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | API status |
| GET | `/health` | No | Health check |
| GET | `/api/v1/products/` | No | List products |
| GET | `/api/v1/products/search?q=` | No | Search products |
| GET | `/api/v1/products/{slug}` | No | Get product by slug |
| POST | `/api/v1/products/` | Admin | Create product |
| PUT | `/api/v1/products/{id}` | Admin | Update product |
| DELETE | `/api/v1/products/{id}` | Admin | Delete product |
| POST | `/api/v1/customers/` | No | Create/get customer |
| GET | `/api/v1/customers/` | Admin | List customers |
| POST | `/api/v1/orders/` | No | Place order |
| GET | `/api/v1/orders/track?order_id=&email=` | No | Track order |
| PATCH | `/api/v1/orders/{id}/status?new_status=` | Admin | Update order status |
| GET | `/api/v1/reviews/?product_id=` | No | List reviews |
| GET | `/api/v1/reviews/summary?product_id=` | No | Get rating summary |
| POST | `/api/v1/reviews/?product_id=` | No | Submit review |
| DELETE | `/api/v1/reviews/{id}` | Admin | Delete review |
| POST | `/api/v1/wishlist/` | No | Add to wishlist |
| DELETE | `/api/v1/wishlist/{slug}?session_key=` | No | Remove from wishlist |
| GET | `/api/v1/wishlist/?session_key=` | No | List wishlist |
| POST | `/api/v1/coupons/validate` | No | Validate coupon |
| GET | `/api/v1/coupons/` | Admin | List coupons |
| POST | `/api/v1/coupons/` | Admin | Create coupon |
| PUT | `/api/v1/coupons/{id}` | Admin | Update coupon |
| DELETE | `/api/v1/coupons/{id}` | Admin | Delete coupon |
| POST | `/api/v1/auth/register` | No | Register user |
| POST | `/api/v1/auth/login` | No | Login |
| GET | `/api/v1/auth/me` | Yes | Current user |

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

76 tests covering all endpoints (Phases 1-12).
