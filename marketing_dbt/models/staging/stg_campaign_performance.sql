WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', 'CAMPAIGN_DAILY_PERFORMANCE') }}
),
renamed AS (
    SELECT
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        CAST(report_date AS DATE) AS performance_date,
        CAST(impressions AS INTEGER) AS impressions,
        CAST(clicks AS INTEGER) AS clicks,
        CAST(spend AS DECIMAL(10,2)) AS daily_spend
    FROM source
)
SELECT * FROM renamed