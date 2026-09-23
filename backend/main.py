import os
from contextlib import asynccontextmanager
from typing import List

import psycopg
from psycopg.rows import dict_row

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ==========================================================
# SETTINGS
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_KEY = os.getenv("LW_ADMIN_KEY", "change-this-admin-key")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")


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
        "A clean, comfortable piece selected for everyday elegance."
    ),
    (
        2,
        "Drop-Shoulder - 2",
        550,
        "images/DS-2.webp",
        "Drop-Shoulder",
        15,
        "NEW",
        "An effortless silhouette designed for comfort and confidence."
    ),
    (
        3,
        "Drop-Shoulder - 3",
        550,
        "images/DS-3.jpg",
        "Drop-Shoulder",
        20,
        "",
        "Simple, versatile and easy to style."
    ),
    (
        4,
        "Drop-Shoulder - 4",
        550,
        "images/DS-4.webp",
        "Drop-Shoulder",
        15,
        "POPULAR",
        "A refined everyday essential with a clean finish."
    ),
    (
        5,
        "Minimalist T-Shirt",
        450,
        "images/TS-1.jpg",
        "T-Shirts",
        25,
        "",
        "Minimal styling and everyday comfort."
    ),
    (
        6,
        "New Arrival T-Shirt",
        450,
        "images/TS-2.jpg",
        "New Arrivals",
        30,
        "NEW",
        "One of the latest pieces in the Lifestyle Wear edit."
    ),
    (
        7,
        "Female Everyday Dress",
        1500,
        "images/FD-1.jpg",
        "Dresses",
        20,
        "BEST",
        "A standout everyday piece from our signature selection."
    ),
    (
        8,
        "Female Everyday Dress - 2",
        1500,
        "images/FD-2.jpg",
        "Dresses",
        25,
        "",
        "Made to be worn, repeated and enjoyed."
    ),
]


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def init_db():

    with get_db() as conn:

        # --------------------------
        # PRODUCTS
        # --------------------------

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

        # --------------------------
        # ORDERS
        # --------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                total INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # --------------------------
        # ORDER ITEMS
        # --------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,

                FOREIGN KEY (order_id)
                    REFERENCES orders(id),

                FOREIGN KEY (product_id)
                    REFERENCES products(id)
            )
        """)

        # --------------------------
        # ADD INITIAL PRODUCTS
        # ONLY IF DATABASE IS EMPTY
        # --------------------------

        result = conn.execute(
            "SELECT COUNT(*) AS count FROM products"
        ).fetchone()

        count = result["count"]

        if count == 0:

            for product in INITIAL_PRODUCTS:

                conn.execute("""
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
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, product)


# ==========================================================
# FASTAPI LIFESPAN
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


# ==========================================================
# FASTAPI APP
# ==========================================================

app = FastAPI(
    title="Lifestyle Wear Stock API",
    version="2.0.0",
    lifespan=lifespan
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

    quantity: int = Field(
        gt=0,
        le=100
    )


class Customer(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=120
    )

    phone: str = Field(
        min_length=1,
        max_length=40
    )

    address: str = Field(
        min_length=1,
        max_length=500
    )

    note: str = Field(
        default="",
        max_length=500
    )


class OrderRequest(BaseModel):

    customer: Customer

    items: List[OrderItem]

    delivery_charge: int = Field(
        default=100,
        ge=0
    )


class StockUpdate(BaseModel):

    stock: int = Field(
        ge=0,
        le=100000
    )


class ProductCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=200
    )

    price: int = Field(
        ge=0
    )

    image: str = Field(
        min_length=1,
        max_length=500
    )

    category: str = Field(
        min_length=1,
        max_length=100
    )

    stock: int = Field(
        ge=0,
        le=100000
    )

    badge: str = Field(
        default="",
        max_length=50
    )

    description: str = Field(
        default="",
        max_length=1000
    )


class ProductUpdate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=200
    )

    price: int = Field(
        ge=0
    )

    image: str = Field(
        min_length=1,
        max_length=500
    )

    category: str = Field(
        min_length=1,
        max_length=100
    )

    stock: int = Field(
        ge=0,
        le=100000
    )

    badge: str = Field(
        default="",
        max_length=50
    )

    description: str = Field(
        default="",
        max_length=1000
    )


# ==========================================================
# BASIC
# ==========================================================

@app.get("/")
def root():

    return {
        "ok": True,
        "service": "Lifestyle Wear Stock API",
        "database": "PostgreSQL"
    }


# ==========================================================
# GET ALL PRODUCTS
# ==========================================================

@app.get("/api/products")
def products():

    with get_db() as conn:

        rows = conn.execute("""
            SELECT *
            FROM products
            ORDER BY id
        """).fetchall()

        return rows


# ==========================================================
# ADMIN AUTHENTICATION
# ==========================================================

def require_admin(key: str | None):

    if not key or key != ADMIN_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid admin key"
        )


# ==========================================================
# ADMIN - SET STOCK
# ==========================================================

@app.put(
    "/api/admin/products/{product_id}/stock"
)
def set_stock(
    product_id: int,
    data: StockUpdate,
    x_admin_key: str | None = Header(default=None)
):

    require_admin(x_admin_key)

    with get_db() as conn:

        cur = conn.execute("""
            UPDATE products
            SET stock = %s
            WHERE id = %s
            RETURNING *
        """, (
            data.stock,
            product_id
        ))

        row = cur.fetchone()

        if row is None:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return row


# ==========================================================
# ADMIN - ADD PRODUCT
# ==========================================================

@app.post("/api/admin/products")
def add_product(
    data: ProductCreate,
    x_admin_key: str | None = Header(default=None)
):

    require_admin(x_admin_key)

    with get_db() as conn:

        result = conn.execute("""
            SELECT COALESCE(MAX(id), 0) + 1 AS next_id
            FROM products
        """).fetchone()

        product_id = result["next_id"]

        row = conn.execute("""
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
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING *
        """, (
            product_id,
            data.name,
            data.price,
            data.image,
            data.category,
            data.stock,
            data.badge,
            data.description
        )).fetchone()

        return row


# ==========================================================
# ADMIN - EDIT PRODUCT
# ==========================================================

@app.put("/api/admin/products/{product_id}")
def edit_product(
    product_id: int,
    data: ProductUpdate,
    x_admin_key: str | None = Header(default=None)
):

    require_admin(x_admin_key)

    with get_db() as conn:

        row = conn.execute("""
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
        """, (
            data.name,
            data.price,
            data.image,
            data.category,
            data.stock,
            data.badge,
            data.description,
            product_id
        )).fetchone()

        if row is None:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return row


# ==========================================================
# ADMIN - REMOVE PRODUCT
# ==========================================================

@app.delete("/api/admin/products/{product_id}")
def remove_product(
    product_id: int,
    x_admin_key: str | None = Header(default=None)
):

    require_admin(x_admin_key)

    with get_db() as conn:

        # Check whether product exists

        product = conn.execute("""
            SELECT *
            FROM products
            WHERE id = %s
        """, (
            product_id,
        )).fetchone()

        if product is None:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )


        # Don't remove a product that is
        # already connected to an order.

        order_item = conn.execute("""
            SELECT id
            FROM order_items
            WHERE product_id = %s
            LIMIT 1
        """, (
            product_id,
        )).fetchone()

        if order_item:

            raise HTTPException(
                status_code=409,
                detail=(
                    "This product cannot be removed "
                    "because it already exists in an order."
                )
            )


        conn.execute("""
            DELETE FROM products
            WHERE id = %s
        """, (
            product_id,
        ))

        return {
            "ok": True,
            "message": "Product removed successfully.",
            "product_id": product_id
        }


# ==========================================================
# CREATE ORDER
# ==========================================================

@app.post("/api/orders")
def create_order(
    order: OrderRequest
):

    if not order.items:

        raise HTTPException(
            status_code=400,
            detail="Order has no items"
        )


    # ------------------------------------------------------
    # MERGE DUPLICATE PRODUCT IDS
    # ------------------------------------------------------

    quantities: dict[int, int] = {}

    for item in order.items:

        quantities[item.product_id] = (
            quantities.get(
                item.product_id,
                0
            )
            + item.quantity
        )


    # ------------------------------------------------------
    # DATABASE TRANSACTION
    # ------------------------------------------------------

    with get_db() as conn:

        try:

            # PostgreSQL transaction starts automatically
            # when the first database command is executed.


            # --------------------------------------------------
            # GET PRODUCTS AND CHECK STOCK
            # --------------------------------------------------

            db_products = {}

            for product_id, qty in quantities.items():

                row = conn.execute("""
                    SELECT *
                    FROM products
                    WHERE id = %s
                    FOR UPDATE
                """, (
                    product_id,
                )).fetchone()


                if row is None:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Product "
                            f"{product_id} not found"
                        )
                    )


                if row["stock"] < qty:

                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"{row['name']} has only "
                            f"{row['stock']} item(s) "
                            f"left in stock."
                        )
                    )


                db_products[product_id] = row


            # --------------------------------------------------
            # CALCULATE TOTAL
            # --------------------------------------------------

            subtotal = sum(
                db_products[product_id]["price"] * qty
                for product_id, qty
                in quantities.items()
            )


            total = (
                subtotal
                + (
                    order.delivery_charge
                    if quantities
                    else 0
                )
            )


            # --------------------------------------------------
            # CREATE ORDER
            # --------------------------------------------------

            order_row = conn.execute("""
                INSERT INTO orders
                (
                    customer_name,
                    customer_phone,
                    customer_address,
                    note,
                    total
                )

                VALUES (%s,%s,%s,%s,%s)

                RETURNING id
            """, (
                order.customer.name,
                order.customer.phone,
                order.customer.address,
                order.customer.note,
                total
            )).fetchone()


            order_id = order_row["id"]


            # --------------------------------------------------
            # ADD ORDER ITEMS + REDUCE STOCK
            # --------------------------------------------------

            for product_id, qty in quantities.items():

                product = db_products[product_id]


                conn.execute("""
                    INSERT INTO order_items
                    (
                        order_id,
                        product_id,
                        quantity,
                        unit_price
                    )

                    VALUES (%s,%s,%s,%s)
                """, (
                    order_id,
                    product_id,
                    qty,
                    product["price"]
                ))


                conn.execute("""
                    UPDATE products

                    SET stock = stock - %s

                    WHERE id = %s
                """, (
                    qty,
                    product_id
                ))


            # --------------------------------------------------
            # GET UPDATED STOCK
            # --------------------------------------------------

            updated_products = conn.execute("""
                SELECT id, stock
                FROM products
                ORDER BY id
            """).fetchall()


            # --------------------------------------------------
            # COMMIT
            # --------------------------------------------------

            conn.commit()


            return {
                "ok": True,
                "order_id": order_id,
                "total": total,
                "products": updated_products
            }


        except HTTPException:

            conn.rollback()

            raise


        except Exception:

            conn.rollback()

            raise