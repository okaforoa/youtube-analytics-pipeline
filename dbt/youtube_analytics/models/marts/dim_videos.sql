-- Dimension: Videos
-- Contains all video attributes
{{ config(materialized='table') }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['video_id']) }} AS video_key,
    video_id,
    title,
    description,
    channel_id,
    channel_title,
    published_at,
    category_id,
    tags,
    duration_iso,
    privacy_status,
    extracted_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at
FROM {{ ref('stg_videos') }}
