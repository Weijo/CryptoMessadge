import sqlite3
import base64
import json
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class ClientKeyStore:
    def __init__(self, db_file: str, password: str) -> None:
        self.db_file = db_file
        self.create_database()

        self.key = self.get_encryption_key(password, "salt")
    
    def create_database(self) -> None:
        self.conn = sqlite3.connect(self.db_file)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS keystore
                    (registration_id INT PRIMARY KEY NOT NULL,
                    device_id INT NOT NULL,
                    username TEXT NOT NULL,
                    identityprivatekey TEXT NOT NULL,
                    identitypublickey TEXT NOT NULL);''')

    def close(self) -> None:
        self.conn.close()

    def get_encryption_key(self, password: str, salt: str):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt.encode(), iterations=480000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def importJson(self, json_string: str) -> list:
        """Reads JSON string and writes to database"""
        data = json.loads(json_string)

        returnData = []
        returnData.append(data.get("registration_id", "FAIL"))
        returnData.append(data.get("device_id", "FAIL"))
        returnData.append(data.get("client_id", "FAIL"))
        returnData.append(data.get("identity_key_private", "FAIL"))
        returnData.append(data.get("identity_key_public", "FAIL"))

        if "FAIL" in returnData:
            return []

        return returnData

    def insert_to_database(self, data: list) -> None:
        if len(data) != 5:
            return

        insert_sql = '''INSERT INTO keystore (registration_id, device_id, username, identityprivatekey, identitypublickey)
                        VALUES (?, ?, ?, ?, ?)'''

        self.conn.execute(insert_sql, (data[0], data[1], data[2], data[3], data[4]))
        self.conn.commit()

    def read_from_database(self, username: str) -> list:
        cursor = self.conn.execute("SELECT * FROM keystore WHERE username=?", (username, ))
        row = cursor.fetchone()
        if not row:
            return []

        return row

    def wrap_key(self, wrapping_key: bytes, key_to_wrap: bytes) -> bytes:
        key = base64.urlsafe_b64decode(wrapping_key)
        return aes_key_wrap(wrapping_key=key, key_to_wrap=key_to_wrap)

    def unwrap_key(self, wrapping_key: bytes, wrapped_key: bytes) -> bytes:
        key = base64.urlsafe_b64decode(wrapping_key)
        return aes_key_unwrap(wrapping_key=key, wrapped_key=wrapped_key)

    def store_key(self, json_string: str):
        data = self.importJson(json_string)

        if data != []:
            # Wrap keys
            data[3] = base64.b64encode(self.wrap_key(self.key, base64.b64decode(data[3]))).decode('utf-8')
            self.insert_to_database(data)



    def retrieve_key(self, username: str) -> str:
        data = self.read_from_database(username)
        if not data:
            return ""

        # Decrypt key
        json_dict = {
            "client_id": data[2],
            "registration_id": data[0],
            "device_id": data[1],
            "identity_key_private": base64.b64encode(self.unwrap_key(self.key, base64.b64decode(data[3].encode()))).decode('utf-8'),
            "identity_key_public": data[4]
        }

        return json.dumps(json_dict)

if __name__ == "__main__":
    
    json_string = '{"client_id": "alice", "registration_id": 4245, "device_id": 1, "identity_key_private": "UAiMJWgnyFjJdK8R5xoR2s7EPlN7jXevcIfEWuMpYmw=", "identity_key_public": "BSxDMvoAVhfIoLQs3qit62QV132Ij9EJ7eW3UeCZvhMy"}'
    print(json_string)
    
    clientstore = ClientKeyStore("client.db", "password")
    try:
        clientstore.store_key(json_string)
    except sqlite3.IntegrityError:
        print("Registration id already exists")
    
    json_data = clientstore.retrieve_key("alice")
    print(json_data)

    json_data = clientstore.retrieve_key("bob")
    if json_data == "":
        print("Not found")
    else:
        print(json_data)