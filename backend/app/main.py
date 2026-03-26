from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal
from .routers import (auth_router, users_router, products_router,
                      suppliers_router, orders_router, tx_router, reports_router)


def seed(db):
    from .models import User, Product, Supplier, Order
    from .services import hash_password

    # Seed users
    if db.query(User).count() == 0:
        db.add_all([
            User(name="Alexandra Chen",  email="admin@stocksmart.io",
                 hashed_pw=hash_password("admin123"),   role="admin",   dept="Management", avatar="AC"),
            User(name="Marcus Webb",     email="manager@stocksmart.io",
                 hashed_pw=hash_password("manager123"), role="manager", dept="Operations", avatar="MW"),
            User(name="Priya Nair",      email="staff@stocksmart.io",
                 hashed_pw=hash_password("staff123"),   role="staff",   dept="Warehouse",  avatar="PN"),
        ])
        db.commit()

    # Seed products
    if db.query(Product).count() == 0:
        db.add_all([
            Product(sku="WM-001", name="Wireless Mouse Pro",   category="Electronics", supplier="NovaTech Dist.",  unit_price=29.99,  stock=150, min_stock=10, reorder_qty=50),
            Product(sku="UH-002", name="USB-C 7-Port Hub",     category="Electronics", supplier="NovaTech Dist.",  unit_price=49.99,  stock=8,   min_stock=15, reorder_qty=30),
            Product(sku="SD-003", name="Standing Desk 160cm",  category="Furniture",   supplier="HomeStyle Inc.",  unit_price=599.99, stock=25,  min_stock=5,  reorder_qty=10),
            Product(sku="MA-004", name="Monitor Arm Dual",     category="Furniture",   supplier="HomeStyle Inc.",  unit_price=89.99,  stock=0,   min_stock=5,  reorder_qty=20),
            Product(sku="MK-005", name="Mechanical Keyboard",  category="Electronics", supplier="TechHub Pro",     unit_price=129.99, stock=60,  min_stock=10, reorder_qty=40),
            Product(sku="WC-006", name="Webcam 4K Ultra HD",   category="Electronics", supplier="TechHub Pro",     unit_price=79.99,  stock=5,   min_stock=8,  reorder_qty=25),
            Product(sku="EC-007", name="Ergonomic Chair Pro",  category="Furniture",   supplier="HomeStyle Inc.",  unit_price=449.99, stock=12,  min_stock=3,  reorder_qty=8),
            Product(sku="HB-008", name="Vitamin D3+K2 90ct",  category="Health",      supplier="WellHub Ltd.",    unit_price=22.50,  stock=71,  min_stock=20, reorder_qty=100),
        ])
        db.commit()

    # Seed suppliers
    if db.query(Supplier).count() == 0:
        db.add_all([
            Supplier(name="NovaTech Dist.",  category="Electronics", contact="sales@novatech.io",    phone="+1-555-0101", status="active"),
            Supplier(name="HomeStyle Inc.",  category="Furniture",   contact="orders@homestyle.com", phone="+1-555-0102", status="active"),
            Supplier(name="TechHub Pro",     category="Electronics", contact="b2b@techhub.co",       phone="+1-555-0103", status="active"),
            Supplier(name="WellHub Ltd.",    category="Health",      contact="supply@wellhub.io",    phone="+1-555-0104", status="inactive"),
        ])
        db.commit()

    # Seed orders
    if db.query(Order).count() == 0:
        db.add_all([
            Order(order_ref="ORD-001", supplier="NovaTech Dist.", items=2, total=3200, status="pending",    order_date="2026-03-18"),
            Order(order_ref="ORD-002", supplier="HomeStyle Inc.", items=1, total=1800, status="processing", order_date="2026-03-17"),
            Order(order_ref="ORD-003", supplier="TechHub Pro",    items=3, total=5100, status="delivered",  order_date="2026-03-15"),
            Order(order_ref="ORD-004", supplier="WellHub Ltd.",   items=1, total=900,  status="pending",    order_date="2026-03-19"),
            Order(order_ref="ORD-005", supplier="NovaTech Dist.", items=4, total=7400, status="delivered",  order_date="2026-03-12"),
            Order(order_ref="ORD-006", supplier="HomeStyle Inc.", items=2, total=2600, status="processing", order_date="2026-03-16"),
        ])
        db.commit()


def create_app() -> FastAPI:
    # Create all DB tables
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="SmartInventory-007 API",
        version="1.0.0",
        description="Role-Based Inventory Management REST API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL, "http://localhost:5173",
                       "http://localhost:3000", "http://127.0.0.1:5173", "null"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register all routers
    for router in [auth_router, users_router, products_router,
                   suppliers_router, orders_router, tx_router, reports_router]:
        app.include_router(router)

    @app.get("/", tags=["Health"])
    def root():
        return {"app": "SmartInventory-007 API", "version": "1.0.0",
                "docs": "/docs", "status": "running"}

    @app.on_event("startup")
    def startup():
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()

    return app


app = create_app()
