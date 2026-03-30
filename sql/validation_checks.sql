SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM experiment_assignments;

SELECT 
    variant,
    COUNT(*) AS users,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM experiment_assignments
GROUP BY variant;

SELECT 
    ea.variant,
    COUNT(DISTINCT e.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0
        / COUNT(DISTINCT ea.user_id) AS conversion_rate
FROM experiment_assignments ea
LEFT JOIN events e 
    ON ea.user_id = e.user_id
GROUP BY ea.variant;

SELECT 
    u.platform,
    u.country,
    ea.variant,
    COUNT(DISTINCT e.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0
        / COUNT(DISTINCT ea.user_id) AS conversion_rate
FROM experiment_assignments ea
JOIN users u ON ea.user_id = u.user_id
LEFT JOIN events e ON ea.user_id = e.user_id
GROUP BY 1,2,3;

SELECT 
    ea.variant,
    AVG(e.revenue) AS avg_order_value
FROM experiment_assignments ea
JOIN events e 
    ON ea.user_id = e.user_id
WHERE e.event_type = 'purchase'
GROUP BY ea.variant;

