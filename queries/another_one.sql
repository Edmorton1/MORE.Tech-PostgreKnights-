SELECT *
FROM users u
WHERE u.id IN (
    SELECT user_id 
    FROM posts p
    WHERE LENGTH(body) > 50
)
AND u.username IN ('admin','user','guest','test','demo','root','manager','editor','author','reader','support','staff')
ORDER BY u.email;