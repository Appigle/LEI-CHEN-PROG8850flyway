import unittest
import mysql.connector
import os
from datetime import datetime


class TestSubscriberCRUD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up database connection for all tests"""
        cls.db_config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('SUBSCRIBER_USER', 'subscriber_user'),
            'password': os.getenv('SUBSCRIBER_PASSWORD', 'SubscriberPass123'),
            'database': 'subscriber_db'
        }

    def setUp(self):
        """Set up fresh connection for each test"""
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up test data created during this test
        if hasattr(self, 'test_subscriber_ids'):
            for subscriber_id in self.test_subscriber_ids:
                self.cursor.execute(
                    "DELETE FROM email_addresses WHERE subscriber_id = %s", (subscriber_id,))
                self.cursor.execute(
                    "DELETE FROM subscribers WHERE id = %s", (subscriber_id,))
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def test_create_subscriber(self):
        """Test creating a new subscriber"""
        self.test_subscriber_ids = []

        # Create subscriber
        name = "Test User Create"
        self.cursor.execute(
            "INSERT INTO subscribers (name) VALUES (%s)",
            (name,)
        )
        self.conn.commit()

        subscriber_id = self.cursor.lastrowid
        self.test_subscriber_ids.append(subscriber_id)

        # Verify subscriber was created
        self.cursor.execute(
            "SELECT name FROM subscribers WHERE id = %s", (subscriber_id,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], name)

    def test_read_subscriber(self):
        """Test reading subscriber data"""
        self.test_subscriber_ids = []

        # Create test subscriber
        name = "Test User Read"
        self.cursor.execute(
            "INSERT INTO subscribers (name) VALUES (%s)",
            (name,)
        )
        self.conn.commit()

        subscriber_id = self.cursor.lastrowid
        self.test_subscriber_ids.append(subscriber_id)

        # Read subscriber
        self.cursor.execute(
            "SELECT id, name, created_at FROM subscribers WHERE id = %s",
            (subscriber_id,)
        )
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], subscriber_id)
        self.assertEqual(result[1], name)
        self.assertIsInstance(result[2], datetime)

    def test_update_subscriber(self):
        """Test updating subscriber data"""
        self.test_subscriber_ids = []

        # Create test subscriber
        original_name = "Test User Original"
        self.cursor.execute(
            "INSERT INTO subscribers (name) VALUES (%s)",
            (original_name,)
        )
        self.conn.commit()

        subscriber_id = self.cursor.lastrowid
        self.test_subscriber_ids.append(subscriber_id)

        # Update subscriber
        updated_name = "Test User Updated"
        self.cursor.execute(
            "UPDATE subscribers SET name = %s WHERE id = %s",
            (updated_name, subscriber_id)
        )
        self.conn.commit()

        # Verify update
        self.cursor.execute(
            "SELECT name FROM subscribers WHERE id = %s", (subscriber_id,))
        result = self.cursor.fetchone()

        self.assertEqual(result[0], updated_name)

    def test_delete_subscriber(self):
        """Test deleting subscriber (cascade should delete emails too)"""
        self.test_subscriber_ids = []

        # Create test subscriber
        name = "Test User Delete"
        self.cursor.execute(
            "INSERT INTO subscribers (name) VALUES (%s)",
            (name,)
        )
        self.conn.commit()

        subscriber_id = self.cursor.lastrowid
        self.test_subscriber_ids.append(subscriber_id)

        # Add email for cascade test
        self.cursor.execute(
            "INSERT INTO email_addresses (subscriber_id, email) VALUES (%s, %s)",
            (subscriber_id, "test.delete@example.com")
        )
        self.conn.commit()

        # Delete subscriber
        self.cursor.execute(
            "DELETE FROM subscribers WHERE id = %s", (subscriber_id,))
        self.conn.commit()

        # Verify deletion
        self.cursor.execute(
            "SELECT COUNT(*) FROM subscribers WHERE id = %s", (subscriber_id,))
        subscriber_count = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(*) FROM email_addresses WHERE subscriber_id = %s", (subscriber_id,))
        email_count = self.cursor.fetchone()[0]

        self.assertEqual(subscriber_count, 0)
        self.assertEqual(email_count, 0)  # Cascade delete should work

        # Remove from cleanup list since we already deleted
        self.test_subscriber_ids.remove(subscriber_id)


class TestEmailCRUD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up database connection for all tests"""
        cls.db_config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('SUBSCRIBER_USER', 'subscriber_user'),
            'password': os.getenv('SUBSCRIBER_PASSWORD', 'SubscriberPass123'),
            'database': 'subscriber_db'
        }

    def setUp(self):
        """Set up fresh connection and test subscriber for each test"""
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()

        # Create test subscriber for email tests
        self.cursor.execute(
            "INSERT INTO subscribers (name) VALUES (%s)",
            ("Email Test Subscriber",)
        )
        self.conn.commit()

        self.test_subscriber_id = self.cursor.lastrowid
        self.test_email_ids = []

    def tearDown(self):
        """Clean up after each test"""
        # Clean up emails first (foreign key constraint)
        for email_id in self.test_email_ids:
            self.cursor.execute(
                "DELETE FROM email_addresses WHERE id = %s", (email_id,))

        # Clean up test subscriber
        self.cursor.execute(
            "DELETE FROM subscribers WHERE id = %s", (self.test_subscriber_id,))
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def test_create_email(self):
        """Test creating email address for subscriber"""
        email = "test.create@example.com"

        # Create email
        self.cursor.execute(
            "INSERT INTO email_addresses (subscriber_id, email) VALUES (%s, %s)",
            (self.test_subscriber_id, email)
        )
        self.conn.commit()

        email_id = self.cursor.lastrowid
        self.test_email_ids.append(email_id)

        # Verify email was created
        self.cursor.execute(
            "SELECT email, subscriber_id FROM email_addresses WHERE id = %s",
            (email_id,)
        )
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], email)
        self.assertEqual(result[1], self.test_subscriber_id)

    def test_read_email(self):
        """Test reading email data"""
        email = "test.read@example.com"

        # Create test email
        self.cursor.execute(
            "INSERT INTO email_addresses (subscriber_id, email) VALUES (%s, %s)",
            (self.test_subscriber_id, email)
        )
        self.conn.commit()

        email_id = self.cursor.lastrowid
        self.test_email_ids.append(email_id)

        # Read email with subscriber info
        self.cursor.execute("""
            SELECT e.id, e.email, e.subscriber_id, s.name 
            FROM email_addresses e
            JOIN subscribers s ON e.subscriber_id = s.id
            WHERE e.id = %s
        """, (email_id,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], email_id)
        self.assertEqual(result[1], email)
        self.assertEqual(result[2], self.test_subscriber_id)
        self.assertEqual(result[3], "Email Test Subscriber")

    def test_update_email(self):
        """Test updating email address"""
        original_email = "test.original@example.com"

        # Create test email
        self.cursor.execute(
            "INSERT INTO email_addresses (subscriber_id, email) VALUES (%s, %s)",
            (self.test_subscriber_id, original_email)
        )
        self.conn.commit()

        email_id = self.cursor.lastrowid
        self.test_email_ids.append(email_id)

        # Update email
        updated_email = "test.updated@example.com"
        self.cursor.execute(
            "UPDATE email_addresses SET email = %s WHERE id = %s",
            (updated_email, email_id)
        )
        self.conn.commit()

        # Verify update
        self.cursor.execute(
            "SELECT email FROM email_addresses WHERE id = %s", (email_id,))
        result = self.cursor.fetchone()

        self.assertEqual(result[0], updated_email)

    def test_delete_email(self):
        """Test deleting email address"""
        email = "test.delete@example.com"

        # Create test email
        self.cursor.execute(
            "INSERT INTO email_addresses (subscriber_id, email) VALUES (%s, %s)",
            (self.test_subscriber_id, email)
        )
        self.conn.commit()

        email_id = self.cursor.lastrowid
        self.test_email_ids.append(email_id)

        # Delete email
        self.cursor.execute(
            "DELETE FROM email_addresses WHERE id = %s", (email_id,))
        self.conn.commit()

        # Verify deletion
        self.cursor.execute(
            "SELECT COUNT(*) FROM email_addresses WHERE id = %s", (email_id,))
        count = self.cursor.fetchone()[0]

        self.assertEqual(count, 0)

        # Remove from cleanup list since we already deleted
        self.test_email_ids.remove(email_id)


if __name__ == '__main__':
    unittest.main()
