import sqlite3
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Define the date format string
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Define the encryption key
def get_encryption_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

# Create an instance of the Fernet class using the derived key
def create_cipher_suite(key):
    cipher_suite = Fernet(key)
    return cipher_suite

# Create a database connection and table
def create_database():
    conn = sqlite3.connect('messageStorage.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages
                 (messageid INT PRIMARY KEY NOT NULL,
                 name TEXT NOT NULL,
                 body TEXT NOT NULL,
                 date TEXT NOT NULL);''')
    return conn

# Define a function to encrypt the message body
def encrypt_body(cipher_suite, body):
    encrypted_body = cipher_suite.encrypt(body.encode())
    return encrypted_body

# Insert data into the table
def insert_messages(conn, messages):
    insert_sql = '''INSERT INTO messages (messageid, name, body, date)
                    VALUES (?, ?, ?, ?)'''
    for message in messages:
        date_str = message[3].strftime(DATE_FORMAT)
        conn.execute(insert_sql, (message[0], message[1], message[2], date_str))
    conn.commit()

# Retrieve the data from the table and print it in a table format
def print_messages(conn):
    cursor = conn.execute("SELECT * FROM messages")
    for row in cursor:
        encrypted_body = row[2].decode()
        date_str = datetime.strptime(row[3], DATE_FORMAT).strftime(DATE_FORMAT)
        print('{0:<10} {1:<10} {2:<20} {3:<20}'.format(row[0], row[1], encrypted_body, date_str))

# Close the database connection
def close_database(conn):
    conn.close()

# Define the main function
def main():
    # Define password and salt
    password = b"password"
    salt = b"salt"

    # Derive the encryption key and create an instance of the Fernet class
    key = get_encryption_key(password, salt)
    cipher_suite = create_cipher_suite(key)

    # Create a database connection and table
    conn = create_database()

    # Insert data into the table
    messages = [
        (1, 'Alice', encrypt_body(cipher_suite, 'Hello'), datetime.now()),
        (2, 'Bob', encrypt_body(cipher_suite, 'How are you?'), datetime.now()),
        (3, 'Charlie', encrypt_body(cipher_suite, 'Nice to meet you'), datetime.now()),
        (4, 'Dave', encrypt_body(cipher_suite, 'Goodbye'), datetime.now()),
    ]
    insert_messages(conn, messages)

    # Retrieve the data from the table and print it in a table format
    print_messages(conn)

    # Close the database connection
    close_database(conn)

# Call the main function
if __name__ == '__main__':
    main()
