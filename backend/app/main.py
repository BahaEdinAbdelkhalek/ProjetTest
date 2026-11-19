from datetime import datetime, timedelta, timezone

import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    create_engine,
    ForeignKey,
    String,
    Integer,
    Float,
    DateTime,
    select,
    func,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demo.db")
SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-before-deployment")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str] = mapped_column(String(180), unique=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    customer: Mapped[Customer] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)


class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    entity: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


Base.metadata.create_all(engine)
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth = OAuth2PasswordBearer(tokenUrl="/api/token")
app = FastAPI(title="StockFlow Demo", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200,http://host.docker.internal:4200",
    ).split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed():
    with SessionLocal() as db:
        for username, password, role in [
            ("admin", "Admin123!", "admin"),
            ("sales", "Sales123!", "sales"),
            ("viewer", "View123!", "viewer"),
        ]:
            if not db.scalar(select(User).where(User.username == username)):
                db.add(
                    User(username=username, password_hash=pwd.hash(password), role=role)
                )
        db.commit()


seed()


def current_user(token: str = Depends(oauth), db: Session = Depends(db_session)):
    try:
        username = jwt.decode(token, SECRET, algorithms=["HS256"]).get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = db.scalar(select(User).where(User.username == username))
    if not user:
        raise HTTPException(401, "Unknown user")
    return user


def require(*roles):
    def check(user=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Insufficient role")
        return user

    return check


def audit(db, user, action, entity, entity_id):
    db.add(
        Audit(actor=user.username, action=action, entity=entity, entity_id=entity_id)
    )


class CustomerIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str


class ProductIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    sku: str = Field(min_length=1, max_length=40)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderIn(BaseModel):
    customer_id: int
    items: list[ItemIn] = Field(min_length=1)


class Transition(BaseModel):
    status: str


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/token")
def token(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session)
):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not pwd.verify(form.password, user.password_hash):
        raise HTTPException(401, "Incorrect username or password")
    return {
        "access_token": jwt.encode(
            {
                "sub": user.username,
                "exp": datetime.now(timezone.utc) + timedelta(hours=2),
            },
            SECRET,
            algorithm="HS256",
        ),
        "token_type": "bearer",
        "role": user.role,
    }


@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"username": user.username, "role": user.role}


@app.get("/api/customers")
def customers(
    q: str = Query("", max_length=120),
    db: Session = Depends(db_session),
    user=Depends(current_user),
):
    return db.scalars(
        select(Customer)
        .where(Customer.name.ilike(f"%{q}%"))
        .order_by(Customer.name)
        .limit(100)
    ).all()


@app.post("/api/customers", status_code=201)
def add_customer(
    data: CustomerIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    row = Customer(**data.model_dump())
    db.add(row)
    try:
        db.flush()
        audit(db, user, "create", "customer", row.id)
        db.commit()
        db.refresh(row)
        return row
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already exists")


@app.put("/api/customers/{cid}")
def update_customer(
    cid: int,
    data: CustomerIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    row = db.get(Customer, cid)
    if not row:
        raise HTTPException(404, "Customer not found")
    row.name = data.name
    row.email = data.email
    audit(db, user, "update", "customer", cid)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already exists")
    return row


@app.delete("/api/customers/{cid}", status_code=204)
def delete_customer(
    cid: int, db: Session = Depends(db_session), user=Depends(require("admin"))
):
    row = db.get(Customer, cid)
    if not row:
        raise HTTPException(404, "Customer not found")
    if db.scalar(
        select(func.count()).select_from(Order).where(Order.customer_id == cid)
    ):
        raise HTTPException(409, "Customer has orders")
    audit(db, user, "delete", "customer", cid)
    db.delete(row)
    db.commit()


@app.get("/api/products")
def products(
    q: str = Query("", max_length=120),
    db: Session = Depends(db_session),
    user=Depends(current_user),
):
    return db.scalars(
        select(Product)
        .where(Product.name.ilike(f"%{q}%") | Product.sku.ilike(f"%{q}%"))
        .order_by(Product.name)
        .limit(100)
    ).all()


@app.post("/api/products", status_code=201)
def add_product(
    data: ProductIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    row = Product(**data.model_dump())
    db.add(row)
    try:
        db.flush()
        audit(db, user, "create", "product", row.id)
        db.commit()
        db.refresh(row)
        return row
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU already exists")


@app.put("/api/products/{pid}")
def update_product(
    pid: int,
    data: ProductIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    row = db.get(Product, pid)
    if not row:
        raise HTTPException(404, "Product not found")
    for k, v in data.model_dump().items():
        setattr(row, k, v)
    audit(db, user, "update", "product", pid)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU already exists")
    return row


@app.delete("/api/products/{pid}", status_code=204)
def delete_product(
    pid: int, db: Session = Depends(db_session), user=Depends(require("admin"))
):
    row = db.get(Product, pid)
    if not row:
        raise HTTPException(404, "Product not found")
    if db.scalar(
        select(func.count()).select_from(OrderItem).where(OrderItem.product_id == pid)
    ):
        raise HTTPException(409, "Product is in an order")
    audit(db, user, "delete", "product", pid)
    db.delete(row)
    db.commit()


@app.post("/api/orders", status_code=201)
def create_order(
    data: OrderIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    if not db.get(Customer, data.customer_id):
        raise HTTPException(404, "Customer not found")
    order = Order(customer_id=data.customer_id, status="draft", total=0)
    db.add(order)
    db.flush()
    total = 0
    for item in data.items:
        p = db.get(Product, item.product_id)
        if not p:
            db.rollback()
            raise HTTPException(404, "Product not found")
        if p.stock < item.quantity:
            db.rollback()
            raise HTTPException(409, f"Insufficient stock for {p.sku}")
        order.items.append(
            OrderItem(product_id=p.id, quantity=item.quantity, unit_price=p.price)
        )
        total += p.price * item.quantity
    order.total = round(total, 2)
    audit(db, user, "create", "order", order.id)
    db.commit()
    return {"id": order.id, "status": order.status, "total": order.total}


@app.get("/api/orders")
def orders(db: Session = Depends(db_session), user=Depends(current_user)):
    found = db.scalars(select(Order).order_by(Order.created_at.desc()).limit(200)).all()
    return [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "customer": o.customer.name,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at,
            "items": [
                {
                    "id": i.id,
                    "product_id": i.product_id,
                    "product": db.get(Product, i.product_id).name,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                }
                for i in o.items
            ],
        }
        for o in found
    ]


@app.get("/api/orders/{oid}")
def get_order(oid: int, db: Session = Depends(db_session), user=Depends(current_user)):
    o = db.get(Order, oid)
    if not o:
        raise HTTPException(404, "Order not found")
    return {
        "id": o.id,
        "customer_id": o.customer_id,
        "customer": o.customer.name,
        "status": o.status,
        "total": o.total,
        "created_at": o.created_at,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "product": db.get(Product, i.product_id).name,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            for i in o.items
        ],
    }


@app.delete("/api/orders/{oid}", status_code=204)
def delete_order(
    oid: int, db: Session = Depends(db_session), user=Depends(require("admin", "sales"))
):
    o = db.get(Order, oid)
    if not o:
        raise HTTPException(404, "Order not found")
    if o.status != "draft":
        raise HTTPException(409, "Only draft orders can be deleted")
    audit(db, user, "delete", "order", oid)
    db.delete(o)
    db.commit()


@app.patch("/api/orders/{oid}/status")
def transition(
    oid: int,
    data: Transition,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    row = db.get(Order, oid)
    if not row:
        raise HTTPException(404, "Order not found")
    allowed = {"draft": "validated", "validated": "closed"}
    if allowed.get(row.status) != data.status:
        raise HTTPException(409, f"Invalid transition {row.status} -> {data.status}")
    if data.status == "validated":
        for item in row.items:
            p = db.get(Product, item.product_id)
            if p.stock < item.quantity:
                raise HTTPException(409, f"Insufficient stock for {p.sku}")
            p.stock -= item.quantity
    row.status = data.status
    audit(db, user, "transition", "order", oid)
    db.commit()
    return {"id": row.id, "status": row.status}


@app.post("/api/orders/{oid}/items", status_code=201)
def add_order_item(
    oid: int,
    data: ItemIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    o = db.get(Order, oid)
    p = db.get(Product, data.product_id)
    if not o:
        raise HTTPException(404, "Order not found")
    if o.status != "draft":
        raise HTTPException(409, "Items can only change on draft orders")
    if not p:
        raise HTTPException(404, "Product not found")
    if p.stock < data.quantity:
        raise HTTPException(409, "Insufficient stock")
    item = OrderItem(
        order_id=oid, product_id=p.id, quantity=data.quantity, unit_price=p.price
    )
    db.add(item)
    o.total = round(o.total + p.price * data.quantity, 2)
    db.flush()
    audit(db, user, "create", "order_item", item.id)
    db.commit()
    return {
        "id": item.id,
        "order_id": oid,
        "product_id": p.id,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
    }


@app.get("/api/order-items/{iid}")
def get_order_item(
    iid: int, db: Session = Depends(db_session), user=Depends(current_user)
):
    item = db.get(OrderItem, iid)
    if not item:
        raise HTTPException(404, "Order item not found")
    return {
        "id": item.id,
        "order_id": item.order_id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
    }


@app.put("/api/order-items/{iid}")
def update_order_item(
    iid: int,
    data: ItemIn,
    db: Session = Depends(db_session),
    user=Depends(require("admin", "sales")),
):
    item = db.get(OrderItem, iid)
    if not item:
        raise HTTPException(404, "Order item not found")
    o = db.get(Order, item.order_id)
    p = db.get(Product, data.product_id)
    if o.status != "draft":
        raise HTTPException(409, "Items can only change on draft orders")
    if not p:
        raise HTTPException(404, "Product not found")
    if p.stock < data.quantity:
        raise HTTPException(409, "Insufficient stock")
    o.total = round(
        o.total - item.quantity * item.unit_price + p.price * data.quantity, 2
    )
    item.product_id = p.id
    item.quantity = data.quantity
    item.unit_price = p.price
    audit(db, user, "update", "order_item", iid)
    db.commit()
    return {
        "id": iid,
        "order_id": o.id,
        "product_id": p.id,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
    }


@app.delete("/api/order-items/{iid}", status_code=204)
def delete_order_item(
    iid: int, db: Session = Depends(db_session), user=Depends(require("admin", "sales"))
):
    item = db.get(OrderItem, iid)
    if not item:
        raise HTTPException(404, "Order item not found")
    o = db.get(Order, item.order_id)
    if o.status != "draft":
        raise HTTPException(409, "Items can only change on draft orders")
    o.total = round(o.total - item.quantity * item.unit_price, 2)
    audit(db, user, "delete", "order_item", iid)
    db.delete(item)
    db.commit()


@app.get("/api/dashboard")
def dashboard(
    status: str | None = Query(None, pattern="^(draft|validated|closed)$"),
    db: Session = Depends(db_session),
    user=Depends(current_user),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    filtered = query.subquery()
    revenue_query = select(func.coalesce(func.sum(filtered.c.total), 0)).where(
        filtered.c.status == "closed"
    )
    return {
        "customers": db.scalar(select(func.count()).select_from(Customer)),
        "products": db.scalar(select(func.count()).select_from(Product)),
        "orders": db.scalar(select(func.count()).select_from(filtered)),
        "revenue": db.scalar(revenue_query),
        "filter_status": status,
        "by_status": dict(
            db.execute(select(Order.status, func.count()).group_by(Order.status)).all()
        ),
    }


@app.get("/api/audit")
def audit_log(db: Session = Depends(db_session), user=Depends(require("admin"))):
    return db.scalars(select(Audit).order_by(Audit.at.desc()).limit(100)).all()
