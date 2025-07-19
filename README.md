# PROG8850Week1Installation

install mysql, python

```bash
ansible-playbook up.yml
```

To use mysql:

```bash
mysql -u root -h 127.0.0.1 -p
```

To run github actions like (notice that the environment variables default for the local case):

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v2

  - name: Install MySQL client
    run: sudo apt-get update && sudo apt-get install -y mysql-client

  - name: Deploy to Database
    env:
      DB_HOST: ${{ secrets.DB_HOST || '127.0.0.1' }}
      DB_USER: ${{ secrets.DB_ADMIN_USER || 'root' }}
      DB_PASSWORD: ${{ secrets.DB_PASSWORD  || 'Secret5555'}}
      DB_NAME: ${{ secrets.DB_NAME || 'mysql' }}
    run: mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < schema_changes.sql
```

locally:

first try

```bash
bin/act
```

then if that doesn't work

```bash
bin/act -P ubuntu-latest=-self-hosted
```

to run in the codespace.

To shut down:

```bash
ansible-playbook down.yml
```

There is also a flyway migration here. To run the migration:

```bash
docker run --rm -v "/workspaces/<repo name>/migrations:/flyway/sql" redgate/flyway -user=root -password=Secret5555 -url=jdbc:mysql://172.17.0.1:3306/flyway_test migrate
```

This is a reproducible mysql setup, with a flyway migration. It is also the start of an example of using flyway and github actions together. Flyway (jdbc) needs the database to exist. The github action creates it if it doesn't exist and flyway takes over from there.

---

# Reproduction Guide

## 🎯 Project Overview

Database migration system with subscriber management, incremental migrations, automated testing, and CI/CD integration.

## 📁 Key Components Added

### **Subscriber System (V2 Migration)**

- New database: `subscriber_db`
- Restricted user: `subscriber_user`
- Tables: `subscribers`, `email_addresses`

### **Incremental Migrations**

- `subscriber_migrations/V1`: Add status column
- `subscriber_migrations/V2`: Add email verification

### **Testing Framework**

- `tests/test_subscriber_crud.py`: CRUD operation tests
- `requirements.txt`: Python dependencies

### **CI/CD Integration**

- Updated GitHub Actions workflow
- Automated deployment with test validation

## 🚀 Reproduction Steps

### **1. Create Subscriber Migration**

```sql
-- migrations/V2__Create_subscriber_system.sql
CREATE DATABASE IF NOT EXISTS subscriber_db;
CREATE USER IF NOT EXISTS 'subscriber_user'@'%' IDENTIFIED BY 'SubscriberPass123';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON subscriber_db.* TO 'subscriber_user'@'%';
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
```

### **2. Create Incremental Migrations**

```sql
-- subscriber_migrations/V1__Add_subscriber_status.sql
USE subscriber_db;
ALTER TABLE subscribers ADD COLUMN status ENUM('active', 'inactive', 'unsubscribed') DEFAULT 'active';

-- subscriber_migrations/V2__Add_email_verification.sql
USE subscriber_db;
ALTER TABLE email_addresses ADD COLUMN is_verified BOOLEAN DEFAULT FALSE, ADD COLUMN verified_at TIMESTAMP NULL;
```

### **3. Create Test Framework**

```python
# tests/test_subscriber_crud.py
import unittest
import mysql.connector
import os

class TestSubscriberCRUD(unittest.TestCase):
    def setUp(self):
        self.conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('SUBSCRIBER_USER', 'subscriber_user'),
            password=os.getenv('SUBSCRIBER_PASSWORD', 'SubscriberPass123'),
            database='subscriber_db'
        )
        self.cursor = self.conn.cursor()

    def test_create_subscriber(self):
        # Test implementation
        pass
```

```txt
# requirements.txt
mysql-connector-python==8.0.33
pytest==7.4.3
```

### **4. Update GitHub Actions**

Add to `.github/workflows/mysql_action.yml`:

```yaml
- name: Run subscriber incremental migrations
  run: docker run flyway migrate (subscriber_migrations)

- name: Run CRUD tests
  run: python -m pytest tests/ -v

- name: Deployment Complete
  run: echo "🚀 Deployment Successfully Completed!"
```
