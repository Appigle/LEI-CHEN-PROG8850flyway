-- V2: Create subscriber database, user, and tables
-- Minimal implementation as requested
CREATE DATABASE IF NOT EXISTS subscriber_db;

CREATE USER IF NOT EXISTS 'subscriber_user'@'%' IDENTIFIED BY 'SubscriberPass123';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER 
ON subscriber_db.* 
TO 'subscriber_user'@'%';

FLUSH PRIVILEGES;

USE subscriber_db;

CREATE TABLE subscribers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subscriber_id INT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id) ON DELETE CASCADE
); 