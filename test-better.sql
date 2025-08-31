-- Создаём таблицы
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    title TEXT,
    body TEXT
);

INSERT INTO users (username, email)
SELECT
    'user_' || g,
    'user_' || g || '@example.com'
FROM generate_series(1, 1000000) AS g;

INSERT INTO posts (user_id, title, body)
SELECT
    floor(random() * 1000000)::INT + 1,  -- случайный user_id
    'Post title ' || g,
    substring(md5(random()::text) || md5(random()::text) from 1 for 100)
FROM generate_series(1, 5000000) AS g;
