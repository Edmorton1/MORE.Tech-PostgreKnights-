SELECT *
FROM users u, posts p
CROSS JOIN posts pp
WHERE LOWER(u.username) = 'admin'
  AND u.id IN (SELECT user_id FROM posts WHERE LENGTH(title) > 10)
  AND EXISTS (
      SELECT 1 
      FROM posts p2
      WHERE p2.user_id = u.id
        AND p2.id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
  )
ORDER BY u.id;