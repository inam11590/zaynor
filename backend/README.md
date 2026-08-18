# ZAYNOR Backend

The FastAPI backend for the ZAYNOR e-commerce platform. Currently at **Phase 13** — admin analytics dashboard is live.

## What Is This?

A Python backend server that powers the ZAYNOR website. It has JWT authentication, an admin dashboard with analytics, order tracking, product search, product reviews, email notifications, database migrations, rate limiting, a product wishlist, and a coupon/discount system.

## Setup (Windows)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

Open `admin.html` — login with `admin@zaynor.com` / `admin123`.

## Admin Dashboard

The admin dashboard (`admin.html`) has 4 tabs:

| Tab | Description |
|-----|-------------|
| **Products** | CRUD products, manage categories and specs |
| **Orders** | View orders, update status (pending → confirmed → shipped → delivered) |
| **Customers** | View registered customers |
| **Analytics** | Revenue stats, top products, recent orders (NEW) |

### Analytics Dashboard

The Analytics tab shows:
- **KPI cards** — total orders, revenue, customers, avg order value, products, pending orders
- **Revenue by day** — daily breakdown with totals, filterable by period (7/30/90/365 days)
- **Top selling products** — ranked by quantity sold with revenue
- **Recent orders** — last 10 orders with status and items

### Analytics Endpoints (Admin Only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/analytics/overview` | Total orders, revenue, customers, products, avg order, status breakdown |
| GET | `/api/v1/analytics/revenue?days=30` | Daily revenue grouped by date |
| GET | `/api/v1/analytics/top-products?limit=5` | Top products by quantity sold |
| GET | `/api/v1/analytics/recent-orders?limit=10` | Most recent orders with items |

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
| GET | `/api/v1/analytics/overview` | Admin | Dashboard overview stats |
| GET | `/api/v1/analytics/revenue?days=30` | Admin | Daily revenue data |
| GET | `/api/v1/analytics/top-products?limit=5` | Admin | Top selling products |
| GET | `/api/v1/analytics/recent-orders?limit=10` | Admin | Recent orders |
| POST | `/api/v1/auth/register` | No | Register user |
| POST | `/api/v1/auth/login` | No | Login |
| GET | `/api/v1/auth/me` | Yes | Current user |

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

81 tests covering all endpoints (Phases 1-13).
