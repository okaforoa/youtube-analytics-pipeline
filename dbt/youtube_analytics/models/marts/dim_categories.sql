-- Dimension: Categories
-- Contains all video category attributes
{{ config(materialized='table') }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['category_id']) }} AS category_key,
    category_id,
    category_name,
    CURRENT_TIMESTAMP() AS dbt_updated_at
FROM {{ ref('stg_categories') }}
