CREATE TABLE users (
    id INT,
    username TEXT,
    email TEXT
);

CREATE TABLE posts (
    id INT,
    user_id INT,
    title TEXT,
    body TEXT
);

INSERT INTO users (id, username, email)
SELECT gs, 
       'user_' || gs, 
       'user_' || gs || '@example.com'
FROM generate_series(1, 1000000) gs;

INSERT INTO posts (id, user_id, title, body)
SELECT gs, 
       (gs % 1000000) + 1, 
       'Post Title ' || gs, 
       'This is the body of post ' || gs
FROM generate_series(1, 5000000) gs;