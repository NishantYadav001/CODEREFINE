CREATE DATABASE IF NOT EXISTS coderefine;
USE coderefine;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo users (password is 'password')
INSERT INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@coderefine.ai', 'password', 'admin'),
('student', 'student@university.edu', 'password', 'student'),
('developer', 'dev@techcorp.com', 'password', 'developer')
ON DUPLICATE KEY UPDATE username=username;