SELECT
    order_id,
    order_revenue
FROM {{ ref('fct_orders') }}
WHERE order_status = 'completed'
  AND order_revenue < 0