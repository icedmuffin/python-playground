CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(225),
    author VARCHAR(225),
    price NUMERIC(10,2)
);