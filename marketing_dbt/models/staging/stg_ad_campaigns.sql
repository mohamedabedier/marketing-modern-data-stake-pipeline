WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', 'AD_CAMPAIGNS') }}
),
renamed AS (
    SELECT
        CAST(_id AS VARCHAR) AS campaign_id,
        CAST(campaign_name AS VARCHAR) AS campaign_name,
        CAST(platform AS VARCHAR) AS ad_platform,
        CAST(daily_budget AS DECIMAL(10,2)) AS campaign_budget,
        CAST(status AS VARCHAR) AS campaign_status
    FROM source
)
SELECT * FROM renamed