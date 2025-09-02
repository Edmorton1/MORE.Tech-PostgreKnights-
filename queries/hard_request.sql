WITH active_users AS (
    SELECT
        u.id AS user_id,
        u.username,
        COUNT(p.id) AS posts_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username
    HAVING COUNT(p.id) > 5
)
SELECT
    au.user_id,
    au.username,
    au.posts_count,
    STRING_AGG(p.title, ', ' ORDER BY p.id) AS recent_post_titles
FROM active_users au
JOIN posts p ON au.user_id = p.user_id
WHERE p.id IN (
    SELECT id
    FROM posts
    WHERE LENGTH(body) > 100
)
GROUP BY au.user_id, au.username, au.posts_count
ORDER BY au.posts_count DESC
LIMIT 10;
