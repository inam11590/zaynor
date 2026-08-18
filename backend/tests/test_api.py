"""Tests for ZAYNOR API endpoints — Phases 1-5.

Each test module uses its own SQLite database so tests never
pollute the production zaynor.db file.
"""
import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Category, Customer, Order, OrderItem, Product
from app.models.user import User
from app.services.auth import hash_password

# ---------------------------------------------------------------------------
# Test database — isolated from production
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///./test_zaynor.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers — generate JWT tokens
# ---------------------------------------------------------------------------
def _get_admin_token() -> str:
    """Create a JWT token for the admin user directly."""
    from app.services.auth import create_access_token
    db = TestSessionLocal()
    admin = db.query(User).filter(User.email == "admin@test.com").first()
    db.close()
    return create_access_token(data={"sub": str(admin.id)})


def _get_user_token() -> str:
    """Create a JWT token for the regular user directly."""
    from app.services.auth import create_access_token
    db = TestSessionLocal()
    user = db.query(User).filter(User.email == "regular@test.com").first()
    db.close()
    return create_access_token(data={"sub": str(user.id)})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def setup_module():
    """Create tables and seed test data."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    # Categories
    cat_perf = Category(name="Perfumes & Attars", slug="perfumes")
    cat_skin = Category(name="Skin Care", slug="skincare")
    db.add_all([cat_perf, cat_skin])
    db.flush()

    # Products
    db.add(
        Product(
            slug="monarch-intense",
            name="Monarch Intense",
            price=4500,
            image="images/perfumes/monarch.png",
            short_description="Test perfume.",
            description="Test full description.",
            specs=json.dumps({"Longevity": "12+ Hours"}),
            category_id=cat_perf.id,
        )
    )
    db.add(
        Product(
            slug="charcoal-face-wash",
            name="Activated Charcoal Face Wash",
            price=1200,
            image="images/skincare/facewash.png",
            short_description="Test face wash.",
            description="Test full description.",
            specs=json.dumps({"Skin Type": "Oily"}),
            category_id=cat_skin.id,
        )
    )

    # Auth users (Phase 5)
    db.add(User(
        email="admin@test.com",
        hashed_password=hash_password("adminpass"),
        is_admin=True,
    ))
    db.add(User(
        email="regular@test.com",
        hashed_password=hash_password("userpass"),
        is_admin=False,
    ))

    db.commit()
    db.close()


# ===========================================================================
# Phase 1 — General endpoints
# ===========================================================================
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ZAYNOR API is running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_accessible():
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible():
    response = client.get("/redoc")
    assert response.status_code == 200


# ===========================================================================
# Phase 2 — Product endpoints
# ===========================================================================
def test_list_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_list_products_filter_by_perfumes():
    response = client.get("/api/v1/products/?category=perfumes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "monarch-intense"


def test_list_products_filter_by_skincare():
    response = client.get("/api/v1/products/?category=skincare")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "charcoal-face-wash"


def test_get_product_by_slug():
    response = client.get("/api/v1/products/monarch-intense")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Monarch Intense"
    assert data["price"] == 4500
    assert data["specs"]["Longevity"] == "12+ Hours"


def test_get_product_not_found():
    response = client.get("/api/v1/products/non-existent-product")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


# ===========================================================================
# Phase 7 — Product search
# ===========================================================================
def test_search_products_by_name():
    response = client.get("/api/v1/products/search?q=Monarch")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["slug"] == "monarch-intense" for p in data)


def test_search_products_by_description():
    response = client.get("/api/v1/products/search?q=charcoal")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["slug"] == "charcoal-face-wash" for p in data)


def test_search_products_no_results():
    response = client.get("/api/v1/products/search?q=xyznonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data == []


# ===========================================================================
# Phase 7 — Order tracking
# ===========================================================================
def test_track_order_success():
    # Create customer + order
    cust = client.post("/api/v1/customers/", json={
        "name": "Track Test",
        "email": "track@example.com",
        "phone": "+923000000000",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    order = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    response = client.get(
        f"/api/v1/orders/track?order_id={order['id']}&email=track@example.com"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order["id"]
    assert data["status"] == "pending"
    assert data["customer_name"] == "Track Test"
    assert len(data["items"]) == 1


def test_track_order_wrong_email():
    # Create the order's customer
    cust = client.post("/api/v1/customers/", json={
        "name": "Wrong Email Track",
        "email": "wrongtrack@example.com",
    }).json()

    # Create a different customer with a different email
    other = client.post("/api/v1/customers/", json={
        "name": "Other Person",
        "email": "otherperson@example.com",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    order = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    # Try tracking with the other customer's email — should fail
    response = client.get(
        f"/api/v1/orders/track?order_id={order['id']}&email=otherperson@example.com"
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_track_order_nonexistent():
    response = client.get("/api/v1/orders/track?order_id=9999&email=nobody@example.com")
    assert response.status_code == 404


# ===========================================================================
# Phase 3 — Customer endpoints
# ===========================================================================
def test_create_customer():
    response = client.post("/api/v1/customers/", json={
        "name": "Ahmed Khan",
        "email": "ahmed@example.com",
        "phone": "+923001234567",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ahmed Khan"
    assert data["email"] == "ahmed@example.com"
    assert data["id"] is not None


def test_create_customer_duplicate_email():
    """Creating a customer with the same email returns the existing one."""
    response = client.post("/api/v1/customers/", json={
        "name": "Ahmed Khan Again",
        "email": "ahmed@example.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ahmed Khan"  # original name preserved


def test_get_customer():
    # First create
    create_res = client.post("/api/v1/customers/", json={
        "name": "Sara Ali",
        "email": "sara@example.com",
    })
    customer_id = create_res.json()["id"]

    response = client.get(f"/api/v1/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "sara@example.com"


def test_get_customer_not_found():
    response = client.get("/api/v1/customers/9999")
    assert response.status_code == 404


# ===========================================================================
# Phase 3 — Order endpoints
# ===========================================================================
def test_create_order():
    # Create customer
    cust = client.post("/api/v1/customers/", json={
        "name": "Order Test",
        "email": "order@example.com",
    }).json()

    # Get product IDs
    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")
    facewash = next(p for p in products if p["slug"] == "charcoal-face-wash")

    # Place order: 2x Monarch + 1x Face Wash = (4500*2) + (1200*1) = 10200
    response = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [
            {"product_id": monarch["id"], "quantity": 2},
            {"product_id": facewash["id"], "quantity": 1},
        ],
        "notes": "Gift wrap please",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["total"] == 10200.0
    assert len(data["items"]) == 2
    assert data["items"][0]["product_name"] == "Monarch Intense"
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price"] == 4500
    assert data["notes"] == "Gift wrap please"


def test_create_order_customer_not_found():
    response = client.post("/api/v1/orders/", json={
        "customer_id": 9999,
        "items": [{"product_id": 1, "quantity": 1}],
    })
    assert response.status_code == 404
    assert "Customer not found" in response.json()["detail"]


def test_create_order_product_not_found():
    cust = client.post("/api/v1/customers/", json={
        "name": "No Product",
        "email": "noprod@example.com",
    }).json()

    response = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": 9999, "quantity": 1}],
    })
    assert response.status_code == 404
    assert "Product with id 9999" in response.json()["detail"]


def test_create_order_empty_items():
    cust = client.post("/api/v1/customers/", json={
        "name": "Empty Order",
        "email": "empty@example.com",
    }).json()

    response = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [],
    })
    assert response.status_code == 400


def test_list_orders():
    response = client.get("/api/v1/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_orders_filter_by_customer():
    # Create a customer and order for filtering
    cust = client.post("/api/v1/customers/", json={
        "name": "Filter Test",
        "email": "filter@example.com",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    })

    response = client.get(f"/api/v1/orders/?customer_id={cust['id']}")
    assert response.status_code == 200
    data = response.json()
    assert all(o["customer_id"] == cust["id"] for o in data)


def test_get_order():
    # Create order
    cust = client.post("/api/v1/customers/", json={
        "name": "Get Order",
        "email": "getorder@example.com",
    }).json()
    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    created = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    response = client.get(f"/api/v1/orders/{created['id']}")
    assert response.status_code == 200
    assert response.json()["total"] == 4500.0


def test_get_order_not_found():
    response = client.get("/api/v1/orders/9999")
    assert response.status_code == 404


# ===========================================================================
# Phase 5 — Authentication
# ===========================================================================
def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "testpass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["is_admin"] is False
    assert "id" in data


def test_register_duplicate_email():
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "anotherpass",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "adminpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@test.com", "password": "pass"},
    )
    assert response.status_code == 401


def test_get_me_authenticated():
    token = _get_admin_token()
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"
    assert response.json()["is_admin"] is True


def test_get_me_unauthenticated():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


# ===========================================================================
# Phase 5 — Admin product CRUD
# ===========================================================================
def test_admin_create_product():
    token = _get_admin_token()
    response = client.post(
        "/api/v1/products/?slug=test-product&name=Test+Product&price=999.99"
        "&image=images/test.png&short_description=Short+desc"
        "&description=Full+description&category_slug=perfumes"
        '&specs={"Key": "Value"}',
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "test-product"
    assert data["price"] == 999.99


def test_non_admin_create_product_forbidden():
    token = _get_user_token()
    response = client.post(
        "/api/v1/products/?slug=nope&name=Nope&price=100"
        "&image=x.png&short_description=No"
        "&description=No&category_slug=perfumes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_product_duplicate_slug():
    token = _get_admin_token()
    response = client.post(
        "/api/v1/products/?slug=monarch-intense&name=Dupe&price=100"
        "&image=x.png&short_description=No"
        "&description=No&category_slug=perfumes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_admin_update_product():
    token = _get_admin_token()
    # Get the test product we created
    products = client.get("/api/v1/products/").json()
    test_prod = next(p for p in products if p["slug"] == "test-product")
    product_id = test_prod["id"]

    response = client.put(
        f"/api/v1/products/{product_id}?name=Updated+Name&price=1234",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 1234


def test_admin_delete_product():
    token = _get_admin_token()
    products = client.get("/api/v1/products/").json()
    test_prod = next(p for p in products if p["slug"] == "test-product")
    product_id = test_prod["id"]

    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Confirm it's gone
    response = client.get(f"/api/v1/products/{test_prod['slug']}")
    assert response.status_code == 404


def test_non_admin_delete_product_forbidden():
    token = _get_user_token()
    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    response = client.delete(
        f"/api/v1/products/{monarch['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ===========================================================================
# Phase 5 — Admin order status update
# ===========================================================================
def test_admin_update_order_status():
    token = _get_admin_token()

    # Create customer + order
    cust = client.post("/api/v1/customers/", json={
        "name": "Status Test",
        "email": "statustest@example.com",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    order = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    # Update status
    response = client.patch(
        f"/api/v1/orders/{order['id']}/status?new_status=shipped",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


def test_admin_update_order_invalid_status():
    token = _get_admin_token()

    cust = client.post("/api/v1/customers/", json={
        "name": "Bad Status",
        "email": "badstatus@example.com",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    order = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    response = client.patch(
        f"/api/v1/orders/{order['id']}/status?new_status=bogus",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_non_admin_update_order_forbidden():
    token = _get_user_token()

    cust = client.post("/api/v1/customers/", json={
        "name": "Forbidden Status",
        "email": "forbidden@example.com",
    }).json()

    products = client.get("/api/v1/products/").json()
    monarch = next(p for p in products if p["slug"] == "monarch-intense")

    order = client.post("/api/v1/orders/", json={
        "customer_id": cust["id"],
        "items": [{"product_id": monarch["id"], "quantity": 1}],
    }).json()

    response = client.patch(
        f"/api/v1/orders/{order['id']}/status?new_status=delivered",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ===========================================================================
# Phase 5 — Admin customer list
# ===========================================================================
def test_admin_list_customers():
    token = _get_admin_token()
    response = client.get(
        "/api/v1/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_non_admin_list_customers_forbidden():
    token = _get_user_token()
    response = client.get(
        "/api/v1/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ===========================================================================
# Phase 8 — Reviews
# ===========================================================================
def _get_product_id():
    """Helper: return the ID of monarch-intense."""
    products = client.get("/api/v1/products/").json()
    return next(p for p in products if p["slug"] == "monarch-intense")["id"]


def _get_product_slug():
    """Helper: return the slug of monarch-intense."""
    return "monarch-intense"


def test_create_review():
    pid = _get_product_id()
    response = client.post(
        f"/api/v1/reviews/?product_id={pid}",
        json={"customer_name": "Ali", "rating": 5, "comment": "Amazing fragrance!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["customer_name"] == "Ali"
    assert data["product_id"] == pid


def test_create_review_no_comment():
    pid = _get_product_id()
    response = client.post(
        f"/api/v1/reviews/?product_id={pid}",
        json={"customer_name": "Sara", "rating": 4},
    )
    assert response.status_code == 201
    assert response.json()["comment"] is None


def test_create_review_invalid_rating():
    pid = _get_product_id()
    response = client.post(
        f"/api/v1/reviews/?product_id={pid}",
        json={"customer_name": "Bad", "rating": 6, "comment": "Nope"},
    )
    assert response.status_code == 422


def test_create_review_product_not_found():
    response = client.post(
        "/api/v1/reviews/?product_id=9999",
        json={"customer_name": "Ghost", "rating": 3},
    )
    assert response.status_code == 404


def test_list_reviews_for_product():
    pid = _get_product_id()
    response = client.get(f"/api/v1/reviews/?product_id={pid}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_rating_summary():
    pid = _get_product_id()
    response = client.get(f"/api/v1/reviews/summary?product_id={pid}")
    assert response.status_code == 200
    data = response.json()
    assert data["review_count"] >= 1
    assert 1.0 <= data["average_rating"] <= 5.0


def test_admin_delete_review():
    token = _get_admin_token()
    pid = _get_product_id()
    review = client.post(
        f"/api/v1/reviews/?product_id={pid}",
        json={"customer_name": "Deleteme", "rating": 1, "comment": "Delete this"},
    ).json()

    response = client.delete(
        f"/api/v1/reviews/{review['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


def test_non_admin_delete_review_forbidden():
    token = _get_user_token()
    pid = _get_product_id()
    review = client.post(
        f"/api/v1/reviews/?product_id={pid}",
        json={"customer_name": "Protected", "rating": 2, "comment": "Keep this"},
    ).json()

    response = client.delete(
        f"/api/v1/reviews/{review['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ─── Phase 9: Email notification tests ────────────────────────────────


def test_order_sends_emails(monkeypatch):
    """Order creation triggers customer confirmation + admin notification emails."""
    from app.services import email as email_mod

    sent: list = []

    def fake_send(to_email, subject, html_body):
        sent.append({"to": to_email, "subject": subject})
        return True

    monkeypatch.setattr(email_mod, "send_email", fake_send)

    cust = client.post(
        "/api/v1/customers/",
        json={"name": "Email Tester", "email": "emailtester@test.com"},
    ).json()
    pid = _get_product_id()

    resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": cust["id"],
            "items": [{"product_id": pid, "quantity": 1}],
        },
    )
    assert resp.status_code == 201

    assert len(sent) == 2
    recipients = [s["to"] for s in sent]
    assert "emailtester@test.com" in recipients
    assert "admin@zaynor.com" in recipients
    subjects = " ".join(s["subject"] for s in sent)
    assert "Order" in subjects


def test_order_email_failure_does_not_block_order(monkeypatch):
    """If email sending fails, the order still succeeds."""
    from app.services import email as email_mod

    def fail_send(to_email, subject, html_body):
        return False

    monkeypatch.setattr(email_mod, "send_email", fail_send)

    cust = client.post(
        "/api/v1/customers/",
        json={"name": "Resilient", "email": "resilient@test.com"},
    ).json()
    pid = _get_product_id()

    resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": cust["id"],
            "items": [{"product_id": pid, "quantity": 1}],
        },
    )
    assert resp.status_code == 201
    assert resp.json()["id"] > 0


def test_email_service_logs_when_disabled():
    """send_email returns True and logs when SMTP is disabled."""
    from app.services.email import send_email
    from app.config import settings

    original = settings.SMTP_ENABLED
    settings.SMTP_ENABLED = False
    try:
        result = send_email("test@test.com", "Test", "<p>Hi</p>")
        assert result is True
    finally:
        settings.SMTP_ENABLED = original


# ─── Phase 10: Rate limiting tests ────────────────────────────────────


def test_rate_limit_not_triggered_under_threshold():
    """Requests under the rate limit do not return 429."""
    for _ in range(3):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nobody@test.com", "password": "x"},
        )
        assert response.status_code != 429


def test_rate_limit_returns_429_when_exceeded():
    """Requests over the rate limit return 429 Too Many Requests."""
    from app.config import settings

    original = settings.RATE_LIMIT_ENABLED
    original_auth = settings.RATE_LIMIT_AUTH
    settings.RATE_LIMIT_ENABLED = True
    settings.RATE_LIMIT_AUTH = "5/minute"
    try:
        for _ in range(6):
            client.post(
                "/api/v1/auth/login",
                data={"username": "wrong@test.com", "password": "wrong"},
            )
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "wrong@test.com", "password": "wrong"},
        )
        assert response.status_code == 429
    finally:
        settings.RATE_LIMIT_ENABLED = original
        settings.RATE_LIMIT_AUTH = original_auth


# ─── Phase 11: Wishlist tests ─────────────────────────────────────────


def _wishlist_session():
    return "test_session_abc123"


def test_add_to_wishlist():
    pid = _get_product_id()
    slug = _get_product_slug()
    resp = client.post(
        "/api/v1/wishlist/",
        json={"session_key": _wishlist_session(), "product_slug": slug},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["product_slug"] == slug
    assert data["product_name"] is not None


def test_add_to_wishlist_idempotent():
    slug = _get_product_slug()
    s = _wishlist_session()
    client.post("/api/v1/wishlist/", json={"session_key": s, "product_slug": slug})
    resp = client.post("/api/v1/wishlist/", json={"session_key": s, "product_slug": slug})
    assert resp.status_code == 201


def test_add_to_wishlist_product_not_found():
    resp = client.post(
        "/api/v1/wishlist/",
        json={"session_key": _wishlist_session(), "product_slug": "nonexistent-slug"},
    )
    assert resp.status_code == 404


def test_list_wishlist():
    s = _wishlist_session()
    resp = client.get(f"/api/v1/wishlist/?session_key={s}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_wishlist_count():
    s = _wishlist_session()
    resp = client.get(f"/api/v1/wishlist/count?session_key={s}")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_check_wishlist():
    s = _wishlist_session()
    slug = _get_product_slug()
    resp = client.get(f"/api/v1/wishlist/check?session_key={s}&product_slug={slug}")
    assert resp.status_code == 200
    assert resp.json()["in_wishlist"] is True


def test_remove_from_wishlist():
    s = _wishlist_session()
    slug = _get_product_slug()
    resp = client.delete(f"/api/v1/wishlist/{slug}?session_key={s}")
    assert resp.status_code == 204

    # Verify removed
    resp = client.get(f"/api/v1/wishlist/check?session_key={s}&product_slug={slug}")
    assert resp.json()["in_wishlist"] is False


def test_remove_from_wishlist_not_found():
    resp = client.delete(f"/api/v1/wishlist/nonexistent?session_key=fake")
    assert resp.status_code == 404


# ─── Phase 12: Coupon tests ───────────────────────────────────────────


def _create_test_coupon(code="TEST20", discount=20, min_order=0, max_uses=None, active=True):
    """Helper: create a coupon via admin endpoint."""
    token = _get_admin_token()
    payload = {"code": code, "discount_percent": discount, "min_order_amount": min_order, "is_active": active}
    if max_uses is not None:
        payload["max_uses"] = max_uses
    resp = client.post(
        "/api/v1/coupons/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()


def test_create_coupon():
    data = _create_test_coupon()
    assert data["code"] == "TEST20"
    assert data["discount_percent"] == 20


def test_create_coupon_duplicate():
    _create_test_coupon(code="DUP10", discount=10)
    token = _get_admin_token()
    resp = client.post(
        "/api/v1/coupons/",
        json={"code": "DUP10", "discount_percent": 10, "min_order_amount": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_validate_coupon_valid():
    _create_test_coupon(code="VALID25", discount=25, min_order=1000)
    resp = client.post(
        "/api/v1/coupons/validate",
        json={"code": "VALID25", "order_amount": 4000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["discount_percent"] == 25
    assert data["discount_amount"] == 1000.0
    assert data["final_amount"] == 3000.0


def test_validate_coupon_below_minimum():
    _create_test_coupon(code="MIN500", discount=10, min_order=5000)
    resp = client.post(
        "/api/v1/coupons/validate",
        json={"code": "MIN500", "order_amount": 2000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "Minimum" in data["message"]


def test_validate_coupon_inactive():
    _create_test_coupon(code="DEAD10", discount=10, active=False)
    resp = client.post(
        "/api/v1/coupons/validate",
        json={"code": "DEAD10", "order_amount": 5000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False


def test_validate_coupon_not_found():
    resp = client.post(
        "/api/v1/coupons/validate",
        json={"code": "NOPE", "order_amount": 5000},
    )
    assert resp.status_code == 404


def test_list_coupons_admin():
    token = _get_admin_token()
    resp = client.get(
        "/api/v1/coupons/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_non_admin_list_coupons_forbidden():
    token = _get_user_token()
    resp = client.get(
        "/api/v1/coupons/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_delete_coupon():
    token = _get_admin_token()
    data = _create_test_coupon(code="DELME", discount=5)
    resp = client.delete(
        f"/api/v1/coupons/{data['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


# ─── Phase 13: Analytics tests ────────────────────────────────────────


def test_analytics_overview():
    token = _get_admin_token()
    resp = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_customers" in data
    assert "avg_order_value" in data
    assert "orders_by_status" in data


def test_analytics_revenue():
    token = _get_admin_token()
    resp = client.get(
        "/api/v1/analytics/revenue?days=30",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_analytics_top_products():
    token = _get_admin_token()
    resp = client.get(
        "/api/v1/analytics/top-products?limit=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_analytics_recent_orders():
    token = _get_admin_token()
    resp = client.get(
        "/api/v1/analytics/recent-orders?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_non_admin_analytics_forbidden():
    token = _get_user_token()
    resp = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
