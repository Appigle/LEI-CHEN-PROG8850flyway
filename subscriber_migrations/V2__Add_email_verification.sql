-- V2: Add email verification tracking
USE subscriber_db;

ALTER TABLE email_addresses 
ADD COLUMN is_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN verified_at TIMESTAMP NULL; 