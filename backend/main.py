from contextlib import asynccontextmanager
import os
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ==========================================================
# SETTINGS
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_KEY = os.getenv("LW_ADMIN_KEY")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

if not ADMIN_KEY:
    raise RuntimeError("LW_ADMIN_KEY environment variable is not set.")


# ==========================================================
# INITIAL PRODUCTS
# ==========================================================

INITIAL_PRODUCTS = [
    (
        1,
        "Drop-Shoulder - 1",
        550,
        "images/DS-1.webp",
        "Drop-Shoulder",
        15,
        "You know",
        "A clean, comfortable piece selected for everyday elegance.",
    ),
    (
        2,
        "Drop-Shoulder - 2",
        550,
        "images/DS-2.webp",
        "Drop-Shoulder",
        15,
        "NEW",
        "An effortless silhouette designed for comfort and confidence.",
    ),
    (
        3,
        "Drop-Shoulder - 3",
        550,
        "images/DS-3.jpg",
        "Drop-Shoulder",
        20,
        "",
        "Simple, versatile and easy to style.",
    ),
    (
        4,
        "Drop-Shoulder - 4",
        550,
        "images/DS-4.webp",
        "Drop-Shoulder",
        15,
        "POPULAR",
        "A refined everyday essential with a clean finish.",
    ),
    (
        5,
        "Minimalist T-Shirt",
        450,
        "images/TS-1.jpg",
        "T-Shirts",
        25,
        "",
        "Minimal styling and everyday comfort.",
    ),
    (
        6,
        "New Arrival T-Shirt",
        450,
        "images/TS-2.jpg",
        "New Arrivals",
        30,
        "NEW",
        "One of the latest pieces in the Lifestyle Wear edit.",
    ),
    (
        7,
        "Female Everyday Dress",
        1500,
        "images/FD-1.jpg",
        "Dresses",
        20,
        "BEST",
        "A standout everyday piece from our signature selection.",
    ),
    (
        8,
        "Female Everyday Dress - 2",
        1500,
        "images/FD-2.jpg",
        "Dresses",
        25,
        "",
        "Made to be worn, repeated and enjoyed.",
    ),
]


# ==========================================================
# DATABASE
# ==========================================================

def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor,
        sslmode="require",
    )


def init_db():

    with get_db() as conn:

        with conn.cursor() as cur:

            # --------------------------
            # PRODUCTS
            # --------------------------

            cur.execute(
                """
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
                """
            )

            # --------------------------
            # ORDERS
            # --------------------------

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    customer_address TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT '',
                    total INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # --------------------------
            # ORDER ITEMS
            # --------------------------

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price INTEGER NOT NULL,

                    FOREIGN KEY (order_id)
                        REFERENCES orders(id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (product_id)
                        REFERENCES products(id)
                )
                """
            )

            # --------------------------
            # INSERT INITIAL PRODUCTS
            # ONLY IF EMPTY
            # --------------------------

            cur.execute(
                "SELECT COUNT(*) AS count FROM products"
            )

            count = cur.fetchone()["count"]

            if count == 0:

                cur.executemany(
                    """
                    INSERT INTO products
                    (
                        id,
                        name,
                        price,
                        image,
                        category,
                        stock,
                        badge,
                        description
                    )
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    INITIAL_PRODUCTS,
                )

        conn.commit()


# ==========================================================
# FASTAPI
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


app = FastAPI(
    title="Lifestyle Wear API",
    version="2.0.0",
    lifespan=lifespan,
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# MODELS
# ==========================================================

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


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: int = Field(ge=0)
    image: str = Field(min_length=1, max_length=500)
    category: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0, le=100000)
    badge: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=2000)


class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: int = Field(ge=0)
    image: str = Field(min_length=1, max_length=500)
    category: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0, le=100000)
    badge: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=2000)


# ==========================================================
# ADMIN AUTHENTICATION
# ==========================================================

def require_admin(key: str | None):

    if not key or key != ADMIN_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid admin key",
        )


# ==========================================================
# HOME / HEALTH CHECK
# ==========================================================

@app.get("/")
def root():

    return {
        "ok": True,
        "service": "Lifestyle Wear API",
        "database": "PostgreSQL",
    }


# ==========================================================
# GET ALL PRODUCTS
# ==========================================================

@app.get("/api/products")
def get_products():

    with get_db() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    name,
                    price,
                    image,
                    category,
                    stock,
                    badge,
                    description
                FROM products
                ORDER BY id
                """
            )

            rows = cur.fetchall()

            return [dict(row) for row in rows]


# ==========================================================
# GET SINGLE PRODUCT
# ==========================================================

@app.get("/api/products/{product_id}")
def get_product(product_id: int):

    with get_db() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            )

            row = cur.fetchone()

            if row is None:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

            return dict(row)


# ==========================================================
# ADMIN — ADD PRODUCT
# ==========================================================

@app.post("/api/admin/products")
def add_product(
    data: ProductCreate,
    x_admin_key: str | None = Header(default=None),
):

    require_admin(x_admin_key)

    with get_db() as conn:

        with conn.cursor() as cur:

            # Generate next product ID
            cur.execute(
                """
                SELECT COALESCE(MAX(id), 0) + 1 AS next_id
                FROM products
                """
            )

            product_id = cur.fetchone()["next_id"]

            cur.execute(
                """
                INSERT INTO products
                (
                    id,
                    name,
                    price,
                    image,
                    category,
                    stock,
                    badge,
                    description
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING *
                """,
                (
                    product_id,
                    data.name,
                    data.price,
                    data.image,
                    data.category,
                    data.stock,
                    data.badge,
                    data.description,
                ),
            )

            product = cur.fetchone()

        conn.commit()

        return {
            "ok": True,
            "message": "Product added successfully.",
            "product": dict(product),
        }


# ==========================================================
# ADMIN — EDIT PRODUCT
# ==========================================================

@app.put("/api/admin/products/{product_id}")
def edit_product(
    product_id: int,
    data: ProductUpdate,
    x_admin_key: str | None = Header(default=None),
):

    require_admin(x_admin_key)

    with get_db() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE products
                SET
                    name = %s,
                    price = %s,
                    image = %s,
                    category = %s,
                    stock = %s,
                    badge = %s,
                    description = %s
                WHERE id = %s
                RETURNING *
                """,
                (
                    data.name,
                    data.price,
                    data.image,
                    data.category,
                    data.stock,
                    data.badge,
                    data.description,
                    product_id,
                ),
            )

            product = cur.fetchone()

            if product is None:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

        conn.commit()

        return {
            "ok": True,
            "message": "Product updated successfully.",
            "product": dict(product),
        }


# ==========================================================
# ADMIN — REMOVE PRODUCT
# ==========================================================

@app.delete("/api/admin/products/{product_id}")
def delete_product(
    product_id: int,
    x_admin_key: str | None = Header(default=None),
):

    require_admin(x_admin_key)

    with get_db() as conn:

        with conn.cursor() as cur:

            # Check product
            cur.execute(
                """
                SELECT *
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            )

            product = cur.fetchone()

            if product is None:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

            # Prevent deleting products that already
            # appear in order history.
            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM order_items
                WHERE product_id = %s
                """,
                (product_id,),
            )

            order_count = cur.fetchone()["count"]

            if order_count > 0:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "This product cannot be removed "
                        "because it exists in previous orders."
                    ),
                )

            cur.execute(
                """
                DELETE FROM products
                WHERE id = %s
                """,
                (product_id,),
            )

        conn.commit()

        return {
            "ok": True,
            "message": "Product removed successfully.",
            "product_id": product_id,
        }


# ==========================================================
# ADMIN — SET STOCK ONLY
# ==========================================================

@app.put("/api/admin/products/{product_id}/stock")
def set_stock(
    product_id: int,
    data: StockUpdate,
    x_admin_key: str | None = Header(default=None),
):

    require_admin(x_admin_key)

    with get_db() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE products
                SET stock = %s
                WHERE id = %s
                RETURNING *
                """,
                (
                    data.stock,
                    product_id,
                ),
            )

            product = cur.fetchone()

            if product is None:

                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

        conn.commit()

        return dict(product)


# ==========================================================
# CREATE ORDER
# ==========================================================

@app.post("/api/orders")
def create_order(order: OrderRequest):

    if not order.items:

        raise HTTPException(
            status_code=400,
            detail="Order has no items",
        )

    # ------------------------------------------------------
    # Merge duplicate product IDs
    # ------------------------------------------------------

    quantities: dict[int, int] = {}

    for item in order.items:

        quantities[item.product_id] = (
            quantities.get(item.product_id, 0)
            + item.quantity
        )

    # ------------------------------------------------------
    # Start PostgreSQL transaction
    # ------------------------------------------------------

    with get_db() as conn:

        try:

            with conn.cursor() as cur:

                # Lock the selected product rows.
                # This is important for shared stock.
                products = {}

                for product_id, qty in quantities.items():

                    cur.execute(
                        """
                        SELECT *
                        FROM products
                        WHERE id = %s
                        FOR UPDATE
                        """,
                        (product_id,),
                    )

                    row = cur.fetchone()

                    if row is None:

                        raise HTTPException(
                            status_code=404,
                            detail=(
                                f"Product {product_id} not found"
                            ),
                        )

                    if row["stock"] < qty:

                        raise HTTPException(
                            status_code=409,
                            detail=(
                                f"{row['name']} has only "
                                f"{row['stock']} item(s) left in stock."
                            ),
                        )

                    products[product_id] = row

                # --------------------------------------------------
                # Calculate subtotal
                # --------------------------------------------------

                subtotal = sum(
                    products[product_id]["price"] * qty
                    for product_id, qty in quantities.items()
                )

                delivery_charge = (
                    order.delivery_charge
                    if quantities
                    else 0
                )

                total = (
                    subtotal
                    + delivery_charge
                )

                # --------------------------------------------------
                # Create order
                # --------------------------------------------------

                cur.execute(
                    """
                    INSERT INTO orders
                    (
                        customer_name,
                        customer_phone,
                        customer_address,
                        note,
                        total
                    )
                    VALUES
                    (%s,%s,%s,%s,%s)
                    RETURNING id
                    """,
                    (
                        order.customer.name,
                        order.customer.phone,
                        order.customer.address,
                        order.customer.note,
                        total,
                    ),
                )

                order_id = cur.fetchone()["id"]

                # --------------------------------------------------
                # Create order items + reduce stock
                # --------------------------------------------------

                for product_id, qty in quantities.items():

                    product = products[product_id]

                    cur.execute(
                        """
                        INSERT INTO order_items
                        (
                            order_id,
                            product_id,
                            quantity,
                            unit_price
                        )
                        VALUES
                        (%s,%s,%s,%s)
                        """,
                        (
                            order_id,
                            product_id,
                            qty,
                            product["price"],
                        ),
                    )

                    cur.execute(
                        """
                        UPDATE products
                        SET stock = stock - %s
                        WHERE id = %s
                        """,
                        (
                            qty,
                            product_id,
                        ),
                    )

                # --------------------------------------------------
                # Get updated stock
                # --------------------------------------------------

                cur.execute(
                    """
                    SELECT id, stock
                    FROM products
                    ORDER BY id
                    """
                )

                updated_products = cur.fetchall()

            # ------------------------------------------------------
            # Commit everything together
            # ------------------------------------------------------

            conn.commit()

            return {
                "ok": True,
                "order_id": order_id,
                "subtotal": subtotal,
                "delivery_charge": delivery_charge,
                "total": total,
                "products": [
                    dict(row)
                    for row in updated_products
                ],
            }

        except HTTPException:

            conn.rollback()
            raise

        except Exception:

            conn.rollback()
            raise


# ==========================================================
# ADMIN — GET ORDERS
# ==========================================================

@app.get("/api/admin/orders")
def get_orders(
    x_admin_key: str | None = Header(default=None),
):

    require_admin(x_admin_key)

    with get_db() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM orders
                ORDER BY created_at DESC
                """
            )

            orders = cur.fetchall()

            result = []

            for order in orders:

                order_data = dict(order)

                cur.execute(
                    """
                    SELECT
                        oi.id,
                        oi.product_id,
                        oi.quantity,
                        oi.unit_price,
                        p.name
                    FROM order_items oi
                    LEFT JOIN products p
                        ON p.id = oi.product_id
                    WHERE oi.order_id = %s
                    ORDER BY oi.id
                    """,
                    (order["id"],),
                )

                order_data["items"] = [
                    dict(item)
                    for item in cur.fetchall()
                ]

                result.append(order_data)

            return result