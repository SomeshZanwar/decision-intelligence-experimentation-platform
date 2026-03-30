SELECT
    experiment_id,
    variant,

    COUNT(DISTINCT user_id) AS users,
    SUM(converted) AS conversions,

    SUM(converted)::float / COUNT(DISTINCT user_id) AS conversion_rate,

    AVG(order_value) AS avg_order_value

FROM {{ ref('int_experiment_base') }}

GROUP BY 1,2