WITH source AS (
    SELECT * FROM {{ source('airbyte_raw', 'CUSTOMERS') }}
),
renamed AS (
    SELECT
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(first_name AS VARCHAR) AS customer_name,
        CAST(email AS VARCHAR) AS email_address,
        CAST(country_code AS VARCHAR) AS country_code,
        CAST(created_at AS TIMESTAMP) AS signup_date
    FROM source
)
SELECT * FROM renamed