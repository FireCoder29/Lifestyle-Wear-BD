from contextlib import asynccontextmanager
from pathlib import Path
import os
import sqlite3
from typing import List

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lifestyle_wear.db"
ADMIN_KEY = os.getenv("LW_ADMIN_KEY", "change-this-admin-key")

# Keep this list synchronized with the products in script.js.
INITIAL_PRODUCTS = [
    (1, "Drop-Shoulder - 1", 550, "images/DS-1.webp", "Drop-Shoulder", 15, "You know", "A clean, comfortable piece selected for everyday elegance."),
    (2, "Drop-Shoulder - 2", 550, "images/DS-2.webp", "Drop-Shoulder", 15, "NEW", "An effortless silhouette designed for comfort and confidence."),
    (3, "Drop-Shoulder - 3", 550, "images/DS-3.jpg", "Drop-Shoulder", 20, "", "Simple, versatile and easy to style."),
    (4, "Drop-Shoulder - 4", 550, "images/DS-4.webp", "Drop-Shoulder", 15, "POPULAR", "A refined everyday essential with a clean finish."),
    (5, "Minimalist T-Shirt", 450, "images/TS-1.jpg", "T-Shirts", 25, "", "Minimal styling and everyday comfort."),
    (6, "New Arrival T-Shirt", 450, "images/TS-2.jpg", "New Arrivals", 30, "NEW", "One of the latest pieces in the Lifestyle Wear edit."),
    (7, "Female Everyday Dress", 1500, "images/FD-1.jpg", "Dresses", 20, "BEST", "A standout everyday piece from our signature selection."),
    (8, "Female Everyday Dress - 2", 1500, "images/FD-2.jpg", "Dresses", 25, "", "Made to be worn, repeated and enjoyed."),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                image TEXT NOT NULL,
                category TEXT NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                badge TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                total INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)

        count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        if count == 0:
            conn.executemany(
                "INSERT INTO products (id,name,price,image,category,stock,badge,description) VALUES (?,?,?,?,?,?,?,?)",
                INITIAL_PRODUCTS,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Lifestyle Wear Stock API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to your GitHub Pages URL when deployed.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=100)


class Customer(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=1, max_length=40)
    address: str = Field(min_length=1, max_length=500)
    note: str = Field(default="", max_length=500)


class OrderRequest(BaseModel):
    customer: Customer
    items: List[OrderItem]
    delivery_charge: int = Field(default=100, ge=0)


class StockUpdate(BaseModel):
    stock: int = Field(ge=0, le=100000)


@app.get("/")
def root():
    return {"ok": True, "service": "Lifestyle Wear Stock API"}


@app.get("/api/products")
def products():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def require_admin(key: str | None):
    if not key or key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


@app.put("/api/admin/products/{product_id}/stock")
def set_stock(product_id: int, data: StockUpdate, x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    with get_db() as conn:
        cur = conn.execute("UPDATE products SET stock = ? WHERE id = ?", (data.stock, product_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row)


@app.post("/api/orders")
def create_order(order: OrderRequest):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order has no items")

    # Merge duplicate product IDs before checking stock.
    quantities: dict[int, int] = {}
    for item in order.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

    with get_db() as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")

            products = {}
            for product_id, qty in quantities.items():
                row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
                if row["stock"] < qty:
                    raise HTTPException(
                        status_code=409,
                        detail=f"{row['name']} has only {row['stock']} item(s) left in stock.",
                    )
                products[product_id] = row

            subtotal = sum(products[pid]["price"] * qty for pid, qty in quantities.items())
            total = subtotal + (order.delivery_charge if quantities else 0)

            cur = conn.execute(
                "INSERT INTO orders (customer_name,customer_phone,customer_address,note,total) VALUES (?,?,?,?,?)",
                (order.customer.name, order.customer.phone, order.customer.address, order.customer.note, total),
            )
            order_id = cur.lastrowid

            for product_id, qty in quantities.items():
                row = products[product_id]
                conn.execute(
                    "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (?,?,?,?)",
                    (order_id, product_id, qty, row["price"]),
                )
                conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (qty, product_id),
                )

            conn.commit()

            updated = conn.execute("SELECT id, stock FROM products ORDER BY id").fetchall()
            return {
                "ok": True,
                "order_id": order_id,
                "total": total,
                "products": [dict(row) for row in updated],
            }

        except HTTPException:
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise
