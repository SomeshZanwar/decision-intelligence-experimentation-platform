SELECT
    experiment_id,
    user_id,
    variant,
    assigned_at
FROM {{ source('raw', 'experiment_assignments') }}