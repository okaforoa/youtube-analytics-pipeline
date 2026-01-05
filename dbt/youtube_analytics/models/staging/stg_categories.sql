-- Staging model: Parse and clean video categories
WITH source AS (
    SELECT 
        RAW_DATA
    FROM {{ source('raw', 'video_categories_raw') }}
),

flattened AS (
    SELECT
        cat.value:id::STRING AS category_id,
        cat.value:snippet.title::STRING AS category_name
    FROM source,
    LATERAL FLATTEN(input => source.RAW_DATA:categories) cat
)

SELECT DISTINCT
    category_id,
    category_name
FROM flattened
WHERE category_id IS NOT NULL
