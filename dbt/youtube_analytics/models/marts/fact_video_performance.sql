-- Fact: Video Performance
-- Contains video metrics and foreign keys to dimensions
{{ config(materialized='table') }}

WITH videos AS (
    SELECT * FROM {{ ref('stg_videos') }}
),

video_dim AS (
    SELECT * FROM {{ ref('dim_videos') }}
),

channel_dim AS (
    SELECT * FROM {{ ref('dim_channels') }}
),

category_dim AS (
    SELECT * FROM {{ ref('dim_categories') }}
)

SELECT
    -- Foreign keys
    vd.video_key,
    cd.channel_key,
    catd.category_key,
    
    -- Date/time
    v.published_at,
    DATE(v.published_at) AS published_date,
    v.extracted_at,
    
    -- Metrics
    v.view_count,
    v.like_count,
    v.comment_count,
    v.like_rate_pct,
    v.comment_rate_pct,
    
    -- Calculated metrics
    CASE 
        WHEN v.like_count > 0 AND v.comment_count > 0 
        THEN v.like_count::FLOAT / v.comment_count
        ELSE 0 
    END AS like_to_comment_ratio,
    
    DATEDIFF(day, v.published_at, v.extracted_at) AS days_since_published,
    
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM videos v
INNER JOIN video_dim vd ON v.video_id = vd.video_id
INNER JOIN channel_dim cd ON v.channel_id = cd.channel_id
LEFT JOIN category_dim catd ON v.category_id = catd.category_id
