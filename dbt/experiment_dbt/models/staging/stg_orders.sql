SELECT
    order_id,
    user_id,
    order_value,
    order_timestamp,
    experiment_id,
    variant
FROM {{ source('raw', 'orders') }}