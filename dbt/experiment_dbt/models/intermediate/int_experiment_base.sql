SELECT
    ea.experiment_id,
    ea.user_id,
    ea.variant,
    u.country,
    u.platform,

    -- conversion flag
    CASE WHEN o.order_id IS NOT NULL THEN 1 ELSE 0 END AS converted,

    -- order value (null if no purchase)
    o.order_value,

    -- timestamps
    ea.assigned_at,
    o.order_timestamp

FROM {{ ref('stg_assignments') }} ea

JOIN {{ ref('stg_users') }} u
    ON ea.user_id = u.user_id

LEFT JOIN {{ ref('stg_orders') }} o
    ON ea.user_id = o.user_id
   AND ea.experiment_id = o.experiment_id