SELECT
    user_id,
    signup_date,
    country,
    platform,
    is_active
FROM {{ source('raw', 'users') }}