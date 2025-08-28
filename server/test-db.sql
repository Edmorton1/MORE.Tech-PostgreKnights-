CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT now()
);

-- 1000 клиентов
INSERT INTO users (name, email)
SELECT
    'User ' || i,
    'User' || i || '@example.com'
FROM generate_series(1,1000) AS s(i);

-- 10 000 заказов
INSERT INTO orders (user_id, total)
SELECT
    (random()*999 + 1)::int,           -- случайный клиент
    (random()*1000)::numeric(10,2)
FROM generate_series(1,10000) AS s(i);
