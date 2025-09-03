WITH user_posts AS (
    SELECT
        u.id AS user_id,
        u.username,
        u.email,
        COUNT(p.id) AS total_posts,
        COUNT(CASE WHEN LENGTH(p.body) > 100 THEN 1 END) AS long_posts_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(p.id) > 5
)
SELECT
    up.user_id,
    up.username,
    up.email,
    up.total_posts,
    up.long_posts_count,
    STRING_AGG(p.title, ', ' ORDER BY p.id) AS recent_post_titles
FROM user_posts up
JOIN posts p ON up.user_id = p.user_id
LEFT JOIN users u2 ON p.user_id = u2.id      -- дополнительный JOIN на users
LEFT JOIN posts p2 ON u2.id = p2.user_id     -- ещё один JOIN на posts
WHERE LENGTH(p.body) > 100
GROUP BY up.user_id, up.username, up.email, up.total_posts, up.long_posts_count
ORDER BY up.total_posts DESC
LIMIT 10;
