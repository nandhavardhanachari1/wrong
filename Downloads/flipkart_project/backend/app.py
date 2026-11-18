import os
from typing import Optional

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(
    title="Flipkart AI Analytics API",
    description="Backend API for Flipkart AI Business Analytics Dashboard",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(DATABASE_URL)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Flipkart AI Analytics API is running",
        "status": "success",
        "docs": "/docs"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "test": result[0]
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# ============================================================
# SUMMARY
# ============================================================

@app.get("/api/summary")
def get_summary():

    query = """
        SELECT
            COALESCE(SUM(total_amount), 0) AS total_revenue,
            COUNT(*) AS total_orders,
            (
                SELECT COUNT(DISTINCT customer_id)
                FROM customers
            ) AS total_customers,
            (
                SELECT COUNT(*)
                FROM reviews
            ) AS total_reviews,
            (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews
            ) AS avg_rating
        FROM orders
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()

    return {
        "total_revenue": float(row[0] or 0),
        "total_orders": int(row[1] or 0),
        "total_customers": int(row[2] or 0),
        "total_reviews": int(row[3] or 0),
        "avg_rating": round(float(row[4] or 0), 2),
    }


# ============================================================
# CUSTOMERS
# ============================================================

@app.get("/api/customers")
def get_customers(
    limit: int = Query(20, ge=1, le=500)
):

    query = """
        SELECT
            customer_id,
            full_name,
            email,
            city,
            state,
            signup_date,
            age,
            gender,
            is_prime_member
        FROM customers
        ORDER BY customer_id
        LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "customer_id": row[0],
            "full_name": row[1],
            "email": row[2],
            "city": row[3],
            "state": row[4],
            "signup_date": str(row[5]) if row[5] else None,
            "age": row[6],
            "gender": row[7],
            "is_prime_member": row[8],
        }
        for row in rows
    ]


# ============================================================
# PRODUCTS
# ============================================================

@app.get("/api/products")
def get_products(
    limit: int = Query(20, ge=1, le=500)
):

    query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category_id,
            c.category_name,
            p.brand,
            p.price,
            p.launch_date
        FROM products p
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        ORDER BY p.product_id
        LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "product_id": row[0],
            "product_name": row[1],
            "category_id": row[2],
            "category_name": row[3],
            "brand": row[4],
            "price": float(row[5] or 0),
            "launch_date": str(row[6]) if row[6] else None,
        }
        for row in rows
    ]


# ============================================================
# REVIEWS
# ============================================================

@app.get("/api/reviews")
def get_reviews(
    limit: int = Query(20, ge=1, le=500)
):

    query = """
        SELECT
            r.review_id,
            r.product_id,
            p.product_name,
            r.customer_id,
            r.review_date,
            r.rating,
            r.review_text,
            r.verified_purchase,
            rs.sentiment_label,
            rs.sentiment_score
        FROM reviews r
        LEFT JOIN products p
            ON r.product_id = p.product_id
        LEFT JOIN review_sentiment rs
            ON r.review_id = rs.review_id
        ORDER BY r.review_id DESC
        LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "review_id": row[0],
            "product_id": row[1],
            "product_name": row[2],
            "customer_id": row[3],
            "review_date": str(row[4]) if row[4] else None,
            "rating": float(row[5] or 0),
            "review_text": row[6],
            "verified_purchase": row[7],
            "sentiment_label": row[8],
            "sentiment_score": float(row[9] or 0) if row[9] is not None else None,
        }
        for row in rows
    ]


# ============================================================
# SENTIMENT SUMMARY
# ============================================================

@app.get("/api/sentiment/category")
def sentiment_category():

    query = """
        SELECT
            sentiment_label,
            COUNT(*) AS total
        FROM review_sentiment
        GROUP BY sentiment_label
        ORDER BY total DESC
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return [
        {
            "sentiment": row[0],
            "count": int(row[1])
        }
        for row in rows
    ]


# ============================================================
# MONTHLY REVENUE
# ============================================================

@app.get("/api/analytics/monthly-revenue")
def monthly_revenue():

    query = """
        SELECT
            TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM') AS month,
            COALESCE(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS orders
        FROM orders
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY DATE_TRUNC('month', order_date)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return [
        {
            "month": row[0],
            "revenue": float(row[1] or 0),
            "orders": int(row[2] or 0)
        }
        for row in rows
    ]


# ============================================================
# TOP PRODUCTS
# ============================================================

@app.get("/api/analytics/top-products")
def top_products(
    limit: int = Query(10, ge=1, le=100)
):

    query = """
        SELECT
            p.product_id,
            p.product_name,
            p.brand,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        GROUP BY
            p.product_id,
            p.product_name,
            p.brand
        ORDER BY revenue DESC
        LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "product_id": row[0],
            "product_name": row[1],
            "brand": row[2],
            "units_sold": int(row[3] or 0),
            "revenue": float(row[4] or 0)
        }
        for row in rows
    ]


# ============================================================
# CHURN RISK
# ============================================================

@app.get("/api/customers/churn-risk")
def get_churn_risk(
    limit: int = Query(10, ge=1, le=100)
):

    query = """
        SELECT
            customer_id,
            full_name,
            city,
            state,
            is_prime_member,
            frequency,
            monetary,
            recency_days,
            avg_sentiment,
            avg_rating,
            churn_probability,
            churn_risk_segment
        FROM customer_churn_scores
        ORDER BY churn_probability DESC
        LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "customer_id": row[0],
            "full_name": row[1],
            "city": row[2],
            "state": row[3],
            "is_prime_member": row[4],
            "frequency": int(row[5] or 0),
            "monetary": float(row[6] or 0),
            "recency_days": int(row[7] or 0),
            "avg_sentiment": float(row[8] or 0),
            "avg_rating": float(row[9] or 0),
            "churn_probability": float(row[10] or 0),
            "churn_risk_segment": row[11],
        }
        for row in rows
    ]


# ============================================================
# RUN LOCALLY
# ============================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )