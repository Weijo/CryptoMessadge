import sqlite3
import base64

class RecordDB:
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file
        self.create_database()

    def create_database(self) -> None:
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS recordDB
                    (username TEXT NOT NULL UNIQUE,
                    record TEXT NOT NULL);''')

    def close(self) -> None:
        self.conn.close()

    def retrieve_record(self, username) -> bytes:
        cursor = self.conn.execute("SELECT record FROM recordDB WHERE username=?", (username, ))
        row = cursor.fetchone()
        if not row:
            return b""

        return base64.b64decode(row[0])
    
    def store_record(self, username: str, record: bytes) -> bool:
        if not username or not record:
            return False 

        insert_sql = '''INSERT INTO recordDB (username, record)
                        VALUES (?, ?)'''
        try:
            self.conn.execute(insert_sql, (username, base64.b64encode(record).decode('UTF-8')))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False