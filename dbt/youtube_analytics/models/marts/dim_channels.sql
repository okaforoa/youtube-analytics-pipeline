-- Dimension: Channels
-- Contains all channel attributes
{{ config(materialized='table') }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['channel_id']) }} AS channel_key,
    channel_id,
    channel_name,
    channel_description,
    channel_created_at,
    subscriber_count,
    total_view_count,
    video_count,
    avg_views_per_video,
    extracted_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at
FROM {{ ref('stg_channels') }}
