import os

os.environ["DATABASE_URL"] = f"sqlite:////tmp/stockflow-test-{os.getpid()}.db"
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def login(name="admin", password="Admin123!"):
    r = client.post("/api/token", data={"username": name, "password": password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health_and_auth_roles():
    assert client.get("/api/health").json()["status"] == "ok"
    h = login("viewer", "View123!")
    assert (
        client.post(
            "/api/customers",
            json={"name": "Denied User", "email": "denied@example.test"},
            headers=h,
        ).status_code
        == 403
    )


def test_customer_uniqueness_and_audit():
    h = login()
    email = "test-" + str(__import__("time").time_ns()) + "@example.test"
    data = {"name": "Test Customer", "email": email}
    assert client.post("/api/customers", json=data, headers=h).status_code == 201
    assert client.post("/api/customers", json=data, headers=h).status_code == 409
    assert any(
        x["action"] == "create" for x in client.get("/api/audit", headers=h).json()
    )


def test_stock_and_status_rules():
    h = login()
    sku = "T" + str(__import__("time").time_ns())
    p = client.post(
        "/api/products",
        json={"name": "Test Widget", "sku": sku, "price": 3.25, "stock": 2},
        headers=h,
    )
    assert p.status_code == 201
    c = client.post(
        "/api/customers",
        json={"name": "Order Customer", "email": sku + "@example.test"},
        headers=h,
    ).json()
    o = client.post(
        "/api/orders",
        json={
            "customer_id": c["id"],
            "items": [{"product_id": p.json()["id"], "quantity": 3}],
        },
        headers=h,
    )
    assert o.status_code == 409
    order = client.post(
        "/api/orders",
        json={
            "customer_id": c["id"],
            "items": [{"product_id": p.json()["id"], "quantity": 1}],
        },
        headers=h,
    )
    oid = order.json()["id"]
    assert (
        client.patch(
            f"/api/orders/{oid}/status", json={"status": "closed"}, headers=h
        ).status_code
        == 409
    )
    assert (
        client.patch(
            f"/api/orders/{oid}/status", json={"status": "validated"}, headers=h
        ).status_code
        == 200
    )
    assert client.get("/api/products?q=" + sku, headers=h).json()[0]["stock"] == 1
    assert (
        client.delete(f"/api/products/{p.json()['id']}", headers=h).status_code == 409
    )
    assert client.delete(f"/api/customers/{c['id']}", headers=h).status_code == 409


def test_customer_product_order_item_crud_and_dashboard_filter():
    h = login()
    suffix = str(__import__("time").time_ns())
    customer = client.post(
        "/api/customers",
        json={"name": "CRUD Customer", "email": suffix + "@example.test"},
        headers=h,
    ).json()
    assert (
        client.put(
            f"/api/customers/{customer['id']}",
            json={
                "name": "Updated CRUD Customer",
                "email": "updated" + suffix + "@example.test",
            },
            headers=h,
        ).status_code
        == 200
    )
    product = client.post(
        "/api/products",
        json={"name": "CRUD Product", "sku": suffix, "price": 5, "stock": 8},
        headers=h,
    ).json()
    duplicate = client.post(
        "/api/products",
        json={"name": "Other Product", "sku": "OTHER" + suffix, "price": 1, "stock": 1},
        headers=h,
    ).json()
    assert (
        client.put(
            f"/api/products/{product['id']}",
            json={
                "name": "CRUD Product",
                "sku": duplicate["sku"],
                "price": 5,
                "stock": 8,
            },
            headers=h,
        ).status_code
        == 409
    )
    order = client.post(
        "/api/orders",
        json={
            "customer_id": customer["id"],
            "items": [{"product_id": product["id"], "quantity": 1}],
        },
        headers=h,
    ).json()
    details = client.get(f"/api/orders/{order['id']}", headers=h).json()
    item_id = details["items"][0]["id"]
    assert client.get(f"/api/order-items/{item_id}", headers=h).status_code == 200
    assert (
        client.put(
            f"/api/order-items/{item_id}",
            json={"product_id": product["id"], "quantity": 2},
            headers=h,
        ).json()["quantity"]
        == 2
    )
    assert client.delete(f"/api/order-items/{item_id}", headers=h).status_code == 204
    extra = client.post(
        f"/api/orders/{order['id']}/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=h,
    )
    assert extra.status_code == 201
    assert (
        client.get("/api/dashboard?status=draft", headers=h).json()["filter_status"]
        == "draft"
    )
    assert client.delete(f"/api/orders/{order['id']}", headers=h).status_code == 204
    assert (
        client.delete(f"/api/customers/{customer['id']}", headers=h).status_code == 204
    )
    assert client.delete(f"/api/products/{product['id']}", headers=h).status_code == 204
    assert (
        client.delete(f"/api/products/{duplicate['id']}", headers=h).status_code == 204
    )
