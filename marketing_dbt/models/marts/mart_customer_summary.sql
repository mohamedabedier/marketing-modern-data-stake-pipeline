WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

fct_orders AS (
    SELECT * FROM {{ ref('fct_orders') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders,
        SUM(CASE WHEN order_status = 'completed' THEN 1 ELSE 0 END) AS total_completed_orders,
        SUM(CASE WHEN order_status = 'completed' THEN order_revenue ELSE 0 END) AS total_lifetime_value
    FROM fct_orders
    GROUP BY customer_id
),

final AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.email_address,
        c.country_code,
        c.signup_date,
        COALESCE(co.total_orders, 0) AS total_orders,
        COALESCE(co.total_completed_orders, 0) AS total_completed_orders,
        COALESCE(co.total_lifetime_value, 0) AS total_lifetime_value
    FROM customers c
    LEFT JOIN customer_orders co ON c.customer_id = co.customer_id
)

SELECT * FROM final