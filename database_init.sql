-- 建立角色資料表
<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS roles (
=======
CREATE TABLE roles (
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- 建立使用者資料表
<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS users (
=======
CREATE TABLE users (
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id)
);

-- 預設角色
<<<<<<< HEAD
INSERT INTO roles (name)
VALUES ('Admin'), ('User')
ON CONFLICT (name) DO NOTHING;
=======
INSERT INTO roles(name)
VALUES
('Admin'),
('User');
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
