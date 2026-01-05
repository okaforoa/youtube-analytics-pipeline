-- Staging model: Parse and clean raw video data
WITH source AS (
    SELECT 
        RAW_DATA,
        LOADED_AT
    FROM {{ source('raw', 'trending_videos_raw') }}
),

flattened AS (
    SELECT
        v.value:id::STRING AS video_id,
        v.value:snippet.title::STRING AS title,
        v.value:snippet.description::STRING AS description,
        v.value:snippet.channelId::STRING AS channel_id,
        v.value:snippet.channelTitle::STRING AS channel_title,
        v.value:snippet.publishedAt::TIMESTAMP AS published_at,
        v.value:snippet.categoryId::STRING AS category_id,
        v.value:snippet.tags::ARRAY AS tags,
        v.value:contentDetails.duration::STRING AS duration_iso,
        COALESCE(v.value:statistics.viewCount::INT, 0) AS view_count,
        COALESCE(v.value:statistics.likeCount::INT, 0) AS like_count,
        COALESCE(v.value:statistics.commentCount::INT, 0) AS comment_count,
        v.value:status.privacyStatus::STRING AS privacy_status,
        source.LOADED_AT AS extracted_at
    FROM source,
    LATERAL FLATTEN(input => source.RAW_DATA:trending_videos) v
)

SELECT 
    video_id,
    title,
    description,
    channel_id,
    channel_title,
    published_at,
    category_id,
    tags,
    duration_iso,
    view_count,
    like_count,
    comment_count,
    privacy_status,
    extracted_at,
    
    -- Calculated fields
    CASE 
        WHEN view_count > 0 THEN ROUND((like_count::FLOAT / view_count) * 100, 2)
        ELSE 0 
    END AS like_rate_pct,
    
    CASE 
        WHEN view_count > 0 THEN ROUND((comment_count::FLOAT / view_count) * 100, 2)
        ELSE 0 
    END AS comment_rate_pct
    
FROM flattened
WHERE video_id IS NOT NULL
