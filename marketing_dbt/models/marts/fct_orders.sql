WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

order_item_summary AS (
    SELECT
        order_id,
        SUM(quantity) AS total_items,
        SUM(quantity * unit_price) AS order_revenue
    FROM order_items
    GROUP BY order_id
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        COALESCE(s.total_items, 0) AS total_items,
        COALESCE(s.order_revenue, 0) AS order_revenue
    FROM orders o
    LEFT JOIN order_item_summary s ON o.order_id = s.order_id
)

SELECT * FROM final