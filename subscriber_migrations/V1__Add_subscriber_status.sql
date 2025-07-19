-- V1: Add status column to track subscriber state
USE subscriber_db;

ALTER TABLE subscribers 
ADD COLUMN status ENUM('active', 'inactive', 'unsubscribed') DEFAULT 'active'; 