SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    session_id
FROM {{ source('raw', 'events') }}