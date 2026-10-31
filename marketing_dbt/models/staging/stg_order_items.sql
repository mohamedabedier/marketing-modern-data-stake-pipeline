WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', 'ORDER_ITEMS') }}
),
renamed AS (
    SELECT
        CAST(order_id AS VARCHAR) AS order_id,
        CAST(product_id AS VARCHAR) AS product_id,
        CAST(quantity AS INTEGER) AS quantity,
        CAST(unit_price AS DECIMAL(10,2)) AS unit_price
    FROM source
)
SELECT * FROM renamed