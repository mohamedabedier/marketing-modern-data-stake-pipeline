"""Generate marketing campaign documents and daily campaign performance.

Campaign IDs and external campaign IDs are intentionally stable so the S3
event generator can reference the same campaigns.
"""
import os
import random
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()
random.seed(int(os.getenv("DATA_SEED", "42")))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "marketing")
INTERVAL_SECONDS = int(os.getenv("MONGO_INTERVAL_SECONDS", "60"))

CAMPAIGNS = [
    {
        "_id": "cmp_1001", "campaign_name": "Summer_Sale_Egypt",
        "platform": "facebook", "account_id": "acc_fb_01",
        "external_campaign_id": "fb_98765", "objective": "conversions",
        "start_date": "2026-07-01", "end_date": "2026-12-31",
        "daily_budget": 5000.0, "currency": "EGP",
        "targeting": {"country": "EG", "age_min": 18, "age_max": 35},
        "creative": {"format": "video", "headline": "Summer Offers"},
        "status": "active"
    },
    {
        "_id": "cmp_1002", "campaign_name": "Search_Always_On",
        "platform": "google", "account_id": "acc_google_01",
        "external_campaign_id": "gads_45678", "objective": "sales",
        "start_date": "2026-07-01", "end_date": "2026-12-31",
        "daily_budget": 3500.0, "currency": "EGP",
        "targeting": {"country": "EG", "keywords": ["wireless mouse", "headphones"]},
        "creative": {"format": "search", "headline": "Shop Electronics"},
        "status": "active"
    },
    {
        "_id": "cmp_1003", "campaign_name": "TikTok_Product_Demo",
        "platform": "tiktok", "account_id": "acc_tt_01",
        "external_campaign_id": "tt_24680", "objective": "traffic",
        "start_date": "2026-07-01", "end_date": "2026-12-31",
        "daily_budget": 2200.0, "currency": "EGP",
        "targeting": {"country": "EG", "age_min": 18, "age_max": 30},
        "creative": {"format": "short_video", "headline": "Tech You Need"},
        "status": "active"
    }
]

def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    campaigns = db["ad_campaigns"]
    performance = db["campaign_daily_performance"]
    campaigns.create_index("external_campaign_id", unique=True)
    performance.create_index([("campaign_id", 1), ("report_date", 1)], unique=True)
    client.admin.command("ping")
    print(f"[MongoDB] Connected to database '{MONGO_DB}'")

    # Upsert campaign definitions once; keep IDs stable across restarts.
    for doc in CAMPAIGNS:
        doc["updated_at"] = datetime.now(timezone.utc)
        campaigns.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)

    while True:
        now = datetime.now(timezone.utc)
        report_date = now.strftime("%Y-%m-%d")
        operations = []
        for campaign in CAMPAIGNS:
            # Incremental counters are simulated, not copied from real ad platforms.
            clicks = random.randint(80, 450)
            impressions = clicks * random.randint(20, 60)
            spend = round(clicks * random.uniform(2.0, 8.0), 2)
            conversions = random.randint(1, max(2, clicks // 10))
            key = {"campaign_id": campaign["_id"], "report_date": report_date}
            operations.append(UpdateOne(
                key,
                {
                    "$setOnInsert": {
                        "campaign_id": campaign["_id"],
                        "external_campaign_id": campaign["external_campaign_id"],
                        "platform": campaign["platform"],
                        "report_date": report_date,
                        "currency": campaign["currency"],
                    },
                    "$inc": {
                        "spend": spend,
                        "impressions": impressions,
                        "clicks": clicks,
                        "reported_conversions": conversions,
                    },
                    "$set": {"updated_at": now}
                },
                upsert=True
            ))
        if operations:
            performance.bulk_write(operations, ordered=False)
        print(f"[MongoDB] Updated daily performance for {len(CAMPAIGNS)} campaigns ({report_date})")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
