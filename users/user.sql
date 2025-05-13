DROP TABLE IF EXISTS user;


CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email_address TEXT UNIQUE NOT NULL,
    employee BOOLEAN NOT NULL,
    password TEXT NOT NULL,
    salt TEXT NOT NULL
);