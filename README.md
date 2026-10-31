# 🚀 Modern Marketing Data Pipeline (ELT)
An end-to-end Modern Data Stack (MDS) implementation featuring data ingestion, cloud data warehousing, automated transformations, and data quality testing.

---

## 🛠️ Tech Stack & Architecture
* **Extract & Load (EL):** Airbyte (Ingesting data from PostgreSQL, MongoDB, and AWS S3).
* **Data Warehouse:** Snowflake (`MARKETING_DW`).
* **Transformation & Modeling (T):** dbt (data build tool) following the **Medallion Architecture**.
* **Data Quality & Testing:** dbt tests (Unique, Not Null, Relationships, Accepted Values, and Custom Business Rules).
* **Version Control & CI/CD:** Git & GitHub.

---

## 🏗️ Architecture Layers (Snowflake Schema)
1. **Bronze Layer (`RAW_DATA`):** Raw ingested data from sources via Airbyte.
2. **Silver Layer (`STAGING`):** Cleaned, type-casted, and standardized staging views (`stg_customers`, `stg_orders`, `stg_order_items`, `stg_ad_campaigns`, `stg_campaign_performance`, `stg_web_events`).
3. **Gold Layer (`MARTS`):** Analytics-ready final models and business aggregations:
   * `fct_orders`: Central fact table combining orders with item details and calculated order revenue (`quantity × unit_price`).
   * `mart_customer_summary`: Customer lifetime value and completed order metrics.
   * `mart_campaign_performance`: Marketing campaign aggregation and ROI analysis.

---

## 🧪 Data Quality Tests
Implements rigorous testing across all layers:
* Uniqueness and Not-Null constraints on primary keys (`customer_id`, `order_id`, `campaign_id`).
* Referential integrity (foreign key relationships).
* Accepted values for order statuses.
* Custom SQL tests ensuring revenue and financial metrics are never negative.

---

## 🔄 How to Rerun the Pipeline
When new data arrives in the source databases or S3:
1. Trigger Airbyte incremental synchronization to load fresh records into Snowflake `RAW_DATA`.
2. Run transformations and update models:
   ```bash
   dbt run
