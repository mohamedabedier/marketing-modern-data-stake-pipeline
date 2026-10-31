# Marketing Intelligence — Source Data Generators

Three Python generators create **related synthetic data** for a marketing analytics capstone:

1. `generate_postgres.py` — CRM customers, orders, and order items.
2. `generate_mongodb.py` — campaign definitions and cumulative daily performance.
3. `generate_s3_events.py` — clickstream JSONL files uploaded to S3.

The IDs are designed to connect across sources:
- PostgreSQL `customers.customer_id` ↔ S3 `customer_id`
- PostgreSQL `customers.anonymous_id` ↔ S3 `anonymous_id`
- MongoDB `ad_campaigns._id` is the internal campaign key
- MongoDB `external_campaign_id` ↔ S3 `utm_campaign`
- PostgreSQL `orders.order_id` ↔ S3 `order_id` for generated purchase events

All data is synthetic. Campaign spend, impressions, clicks, and reported conversions are simulated, not real advertising-platform data.

## 1. Prerequisites

- Python 3.10+
- PostgreSQL and MongoDB running and reachable
- An AWS S3 bucket already created
- AWS credentials configured with permission to write objects to that bucket

Use a dedicated local/dev database. These scripts create tables and collections and insert synthetic records.

## 2. Install

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your PostgreSQL password and S3 bucket name. Do not commit `.env` or AWS credentials to GitHub.

For AWS credentials, prefer an AWS profile or environment/role-based credentials rather than hardcoding access keys. The identity running the S3 generator needs `s3:PutObject` on the target prefix and permission to inspect the bucket.

## 3. Start order

Open three terminals in the project directory and run:

```bash
python generate_postgres.py
```

```bash
python generate_mongodb.py
```

```bash
python generate_s3_events.py
```

Start PostgreSQL and MongoDB generators first. The S3 generator reads their IDs to make the event data consistent. Stop any generator with `Ctrl+C`.

## 4. What gets generated?

### PostgreSQL
- Stable customers with IDs `1..CUSTOMER_COUNT`
- New orders every `POSTGRES_INTERVAL_SECONDS`
- One to three order items per order
- Orders may be completed, pending, or cancelled

### MongoDB
- Three stable campaign documents
- One performance document per campaign per report date
- Spend, impressions, clicks, and reported conversions increase each cycle

### S3
- JSON Lines files under `S3_PREFIX/event_date=YYYY-MM-DD/`
- Events: `page_view`, `view_item`, `add_to_cart`, `begin_checkout`, and some `purchase` events
- Purchase events use existing completed PostgreSQL order IDs

## 5. DBeaver, Airbyte, Snowflake, and dbt

- **DBeaver** is a SQL client: use it to inspect PostgreSQL and Snowflake. It does not host databases or MongoDB itself; MongoDB access may require a compatible driver/edition or another MongoDB client.
- **Airbyte** can ingest PostgreSQL and MongoDB into Snowflake through supported source/destination connectors. Configure each connector according to its current schema and sync options.
- For S3, configure an Airbyte S3 source with the bucket, prefix, file format (JSONL/NDJSON), and AWS access. Connector support and incremental behavior depend on the chosen connector and configuration.
- **dbt** should transform the landed Snowflake tables into staging, intermediate, and marts models.

## 6. Important modeling caveats

- `campaign_daily_performance` stores simulated platform-reported metrics. These conversions are not guaranteed to match PostgreSQL orders.
- A generated purchase event links to an actual completed order, but its campaign is selected for demo attribution. Do not present that attribution as causal truth.
- A real attribution model needs a defined lookback window and identity/session rules.
- `orders.total_amount` includes tax and shipping in this demo. Decide whether your revenue metric should include them and handle cancelled/refunded orders consistently.
- The performance generator increments the current day's counters. If you restart it, counters continue to increase; this is intentional for a continuously running simulation.
- These are local development generators, not production-grade ingestion services. Add logging, retries, checkpoints, schema versioning, and idempotency before production use.
# marketing-modern-data-stake-pipeline
