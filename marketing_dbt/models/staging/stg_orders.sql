WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', 'ORDERS') }}
),
renamed AS (
    SELECT
        CAST(order_id AS VARCHAR) AS order_id,
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(order_timestamp AS TIMESTAMP) AS order_date,
        LOWER(CAST(order_status AS VARCHAR)) AS order_status
    FROM source
)
SELECT * FROM renamed