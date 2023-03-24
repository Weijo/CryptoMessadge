import sqlite3
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Define the datetime format string
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# Define the encryption key
def get_encryption_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


# Create an instance of the Fernet class using the derived key
def create_cipher_suite(key):
    cipher_suite = Fernet(key)
    return cipher_suite


# def create_database():
#     conn = sqlite3.connect('messageStorage.db')
#     conn.execute('''CREATE TABLE IF NOT EXISTS messages
#                  (messageid INT PRIMARY KEY NOT NULL,
#                  name TEXT NOT NULL,
#                  body TEXT NOT NULL,
#                  datetime TEXT NOT NULL);''')
#     return conn

# connect to database (create table if doesn't exist)
def connect_to_database(username):
    conn = sqlite3.connect(username + '_messageStorage.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages
                 (messageId INT PRIMARY KEY NOT NULL,
                 convo_id TEXT NOT NULL,
                 sender TEXT NOT NULL,
                 recipient TEXT NOT NULL,
                 encrypted_message TEXT NOT NULL,
                 datetime TEXT NOT NULL);''')
    return conn


# Define a function to encrypt the message body
def encrypt_body(cipher_suite, body):
    encrypted_body = cipher_suite.encrypt(body.encode())
    return encrypted_body


def decrypt_body(cipher_suite, body):
    decrypted_body = cipher_suite.decrypt(body.encode())
    return decrypted_body


# Insert data into the table
def insert_messages(conn, messages):
    insert_sql = '''INSERT INTO messages (messageId, convo_id, sender, recipient, encrypted_message, datetime)
                    VALUES (?, ?, ?, ?, ?, ?)'''
    for message in messages:
        datetime_str = message[5].strftime(DATETIME_FORMAT)
        conn.execute(insert_sql, (message[0], message[1], message[2], message[3], message[4], datetime_str))
    conn.commit()


# Retrieve the data from the table and print it in a table format
def print_messages(conn):
    cursor = conn.execute("SELECT * FROM messages")
    for row in cursor:
        encrypted_message = row[4]
        datetime_str = datetime.strptime(row[5], DATETIME_FORMAT).strftime(DATETIME_FORMAT)
        print('{0:<10} {1:<10} {2:<10} {3:<20} {4:<20} {5:<20}'.format(row[0], row[1], row[2], row[3], encrypted_message, datetime_str))


def get_latest_message_id(conn):
    cursor = conn.execute("SELECT messageId FROM messages ORDER BY messageId DESC LIMIT 1")
    for row in cursor:
        return row[0]


def database_empty(conn):
    cursor = conn.execute("SELECT * FROM messages")
    db_result = cursor.fetchall()
    if len(db_result) == 0:
        return True
    else:
        return False


# Close the database connection
def close_database(conn):
    conn.close()
