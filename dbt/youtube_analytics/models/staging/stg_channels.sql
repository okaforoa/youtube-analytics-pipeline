-- Staging model: Parse and clean raw channel data
WITH source AS (
    SELECT 
        RAW_DATA,
        LOADED_AT
    FROM {{ source('raw', 'trending_videos_raw') }}
),

flattened AS (
    SELECT
        c.value:id::STRING AS channel_id,
        c.value:snippet.title::STRING AS channel_name,
        c.value:snippet.description::STRING AS channel_description,
        c.value:snippet.publishedAt::TIMESTAMP AS channel_created_at,
        c.value:statistics.subscriberCount::INT AS subscriber_count,
        c.value:statistics.viewCount::BIGINT AS total_view_count,
        c.value:statistics.videoCount::INT AS video_count,
        source.LOADED_AT AS extracted_at
    FROM source,
    LATERAL FLATTEN(input => source.RAW_DATA:channels) c
)

SELECT DISTINCT
    channel_id,
    channel_name,
    channel_description,
    channel_created_at,
    subscriber_count,
    total_view_count,
    video_count,
    extracted_at,
    
    -- Calculated field
    CASE 
        WHEN video_count > 0 THEN ROUND(total_view_count::FLOAT / video_count, 0)
        ELSE 0 
    END AS avg_views_per_video
    
FROM flattened
WHERE channel_id IS NOT NULL
