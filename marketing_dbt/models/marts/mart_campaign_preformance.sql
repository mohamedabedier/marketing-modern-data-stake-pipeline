WITH campaigns AS (
    SELECT * FROM {{ ref('stg_ad_campaigns') }}
),

performance AS (
    SELECT * FROM {{ ref('stg_campaign_performance') }}
),

campaign_summary AS (
    SELECT
        campaign_id,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(daily_spend) AS total_spend
    FROM performance
    GROUP BY campaign_id
),

final AS (
    SELECT
        c.campaign_id,
        c.campaign_name,
        c.ad_platform,
        c.campaign_status,
        c.campaign_budget,
        COALESCE(cs.total_impressions, 0) AS total_impressions,
        COALESCE(cs.total_clicks, 0) AS total_clicks,
        COALESCE(cs.total_spend, 0) AS total_spend
    FROM campaigns c
    LEFT JOIN campaign_summary cs ON c.campaign_id = cs.campaign_id
)

SELECT * FROM final