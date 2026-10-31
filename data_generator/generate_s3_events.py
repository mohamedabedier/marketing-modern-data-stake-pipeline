"""Generate clickstream JSONL batches and upload them to S3.

Events use the same stable customer and campaign identifiers as the other
two generators. For purchase events, order_id is selected from PostgreSQL,
so event data can be reconciled with real generated orders.
"""
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from io import BytesIO
import boto3
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
random.seed(int(os.getenv("DATA_SEED", "42")))

PG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "marketing_crm"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
}
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "marketing")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PREFIX = os.getenv("S3_PREFIX", "raw/web_events")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
INTERVAL_SECONDS = int(os.getenv("S3_INTERVAL_SECONDS", "90"))
EVENTS_PER_BATCH = int(os.getenv("EVENTS_PER_BATCH", "100"))

def get_reference_data():
    with psycopg2.connect(**PG) as conn, conn.cursor() as cur:
        cur.execute("SELECT customer_id, anonymous_id FROM customers ORDER BY customer_id")
        customers = [{"customer_id": r[0], "anonymous_id": r[1]} for r in cur.fetchall()]
        cur.execute("""
            SELECT order_id, customer_id, order_timestamp, total_amount, currency
            FROM orders WHERE order_status = 'completed'
            ORDER BY order_id DESC LIMIT 500
        """)
        orders = [
            {"order_id": r[0], "customer_id": r[1],
             "order_timestamp": r[2].astimezone(timezone.utc).isoformat(),
             "total_amount": float(r[3]), "currency": r[4]}
            for r in cur.fetchall()
        ]
    mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    campaigns = list(mongo[MONGO_DB]["ad_campaigns"].find(
        {"status": "active"},
        {"_id": 1, "external_campaign_id": 1, "platform": 1}
    ))
    mongo.close()
    if not customers:
        raise RuntimeError("No customers found. Start generate_postgres.py first.")
    if not campaigns:
        raise RuntimeError("No campaigns found. Start generate_mongodb.py first.")
    return customers, orders, campaigns

def build_events(customers, orders, campaigns):
    now = datetime.now(timezone.utc)
    rows = []
    page_types = ["home", "category", "product", "landing_page", "cart"]
    campaign = random.choice(campaigns)
    customer = random.choice(customers)
    session_id = "sess_" + uuid.uuid4().hex[:16]
    common = {
        "anonymous_id": customer["anonymous_id"],
        "customer_id": customer["customer_id"],
        "session_id": session_id,
        "utm_source": campaign["platform"],
        "utm_medium": "paid_social" if campaign["platform"] in ("facebook", "tiktok") else "paid_search",
        "utm_campaign": campaign["external_campaign_id"],
        "utm_content": "creative_" + str(random.randint(1, 5)),
        "referrer": f"https://{campaign['platform']}.example/",
        "currency": "EGP"
    }
    funnel = ["page_view", "view_item", "add_to_cart", "begin_checkout"]
    product_id = random.choice([1001, 1002, 1003, 1004, 1005])
    for i, event_name in enumerate(funnel):
        event = {
            "event_id": "evt_" + uuid.uuid4().hex,
            "event_timestamp": now.isoformat(),
            **common,
            "event_name": event_name,
            "page_url": f"https://shop.example.com/{random.choice(page_types)}",
            "page_type": page_types[min(i, len(page_types)-1)],
            "product_id": product_id if event_name in ("view_item", "add_to_cart") else None,
            "quantity": 1 if event_name == "add_to_cart" else None,
            "event_value": None
        }
        rows.append(event)

    # Tie some purchase events to completed PostgreSQL orders, never invent order IDs.
    if orders and random.random() < 0.35:
        order = random.choice(orders)
        order_customer = next((c for c in customers if c["customer_id"] == order["customer_id"]), None)
        if order_customer:
            purchase_campaign = random.choice(campaigns)
            rows.append({
                "event_id": "evt_" + uuid.uuid4().hex,
                "event_timestamp": order["order_timestamp"],
                "anonymous_id": order_customer["anonymous_id"],
                "customer_id": order["customer_id"],
                "session_id": "sess_purchase_" + str(order["order_id"]),
                "event_name": "purchase",
                "page_url": "https://shop.example.com/order-confirmation",
                "page_type": "confirmation",
                "utm_source": purchase_campaign["platform"],
                "utm_medium": "paid_social" if purchase_campaign["platform"] in ("facebook", "tiktok") else "paid_search",
                "utm_campaign": purchase_campaign["external_campaign_id"],
                "utm_content": "purchase_attribution_demo",
                "referrer": None,
                "product_id": None,
                "quantity": None,
                "event_value": order["total_amount"],
                "currency": order["currency"],
                "order_id": order["order_id"]
            })
    return rows

def upload_jsonl(s3, rows):
    now = datetime.now(timezone.utc)
    key = f"{S3_PREFIX.strip('/')}/event_date={now:%Y-%m-%d}/events_{now:%H%M%S}_{uuid.uuid4().hex[:8]}.jsonl"
    body = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows).encode("utf-8")
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/x-ndjson")
    print(f"[S3] Uploaded {len(rows)} events to s3://{S3_BUCKET}/{key}")

def main():
    if not S3_BUCKET:
        raise RuntimeError("Set S3_BUCKET in .env before running this script.")
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.head_bucket(Bucket=S3_BUCKET)
    print(f"[S3] Bucket ready: {S3_BUCKET}")
    while True:
        customers, orders, campaigns = get_reference_data()
        rows = []
        # Generate batches of small sessions, all referencing the same source entities.
        for _ in range(max(1, EVENTS_PER_BATCH // 4)):
            rows.extend(build_events(customers, orders, campaigns))
        upload_jsonl(s3, rows)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
