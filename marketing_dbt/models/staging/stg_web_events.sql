WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', '"BRONZE/WEB_EVENTS/"') }}
),
renamed AS (
    SELECT
        CAST(event_id AS VARCHAR) AS event_id,
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(event_name AS VARCHAR) AS event_type,
        CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
        CAST(page_url AS VARCHAR) AS page_url
    FROM source
)
SELECT * FROM renamed