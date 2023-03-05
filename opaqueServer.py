import opaque
import base64
import sqlite3
import json
from Crypto.Cipher import ChaCha20_Poly1305

class opaqueServer:
    def __init__(self) -> None:
        # self.dbfile = "opaque.db"
        # self.initDatabase()
        self.users = {}
        self.context = "CryptoMessadge"

    def handle_registration(self, request, request_data) -> None:
        # Decode Step 1:
        print(f"{request_data=}")
        dictionary = json.loads(request_data.decode('utf-8'))
        username = dictionary.get("id", "")
        message_base64 = dictionary.get("message", "")

        # Abort if no request was received
        if message_base64 == "":
            return 

        message = base64.b64decode(message_base64)

        # Step 2: The server responds to the registration request
        # TODO: Add long term server key
        # secS, pub = opaque.CreateRegistrationResponse(message, skS) 
        secS, pub = opaque.CreateRegistrationResponse(message)

        pub_base64 = base64.b64encode(pub)
        print(f"{pub_base64=}")
        request.sendall(pub_base64)

        # Receive Step 3
        record_b64 = request.recv(1024).strip()
        record = base64.b64decode(record_b64)
        print(f"{record_b64=}")

        # Step 4: The server finalizes the user's record
        rec1 = opaque.StoreUserRecord(secS, record)

        # Store rec1 in database
        self.users[username] = rec1
    
    def handle_login(self, request, request_data) -> bool:
        # Decode Step 1
        print(f"{request_data=}")
        dictionary = json.loads(request_data.decode('utf-8'))
        username = dictionary.get("id", "")
        message_base64 = dictionary.get("message", "")

        # Abort if no request was received
        if message_base64 == "":
            return 

        pub = base64.b64decode(message_base64)

        # Step 2: The server responds to the credential request
        
        # Fetch record
        rec = self.users.get(username, b"")
        if rec == b"":
            return
        
        ids = opaque.Ids(username, "server")
        resp, sk, secS = opaque.CreateCredentialResponse(pub, rec, ids, self.context)

        response_b64 = base64.b64encode(resp)
        request.sendall(response_b64) 

        # Step 4: Authenticate user
        authU_b64 = request.recv(1024).strip()
        print(f"{authU_b64=}")
        authU = base64.b64decode(authU_b64)

        try:
            opaque.UserAuth(secS, authU)
        except:
            request.sendall(b"False")
            return False

        request.sendall(b"True")
        self.sk = sk
        return True

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt using ChaCha20_Poly1305
        """
        # OPAQUE's key is 64 bytes
        key = self.sk[:32]
        header = self.context.encode()
        cipher = ChaCha20_Poly1305.new(key=key)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        jk = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        jv = [ base64.b64encode(x).decode('utf-8') for x in (cipher.nonce, header, ciphertext, tag) ]
        result = json.dumps(dict(zip(jk, jv)))
        return result

    def decrypt(self, json_input: bytes) -> bytes:
        """
        Decryption using ChaCha20_Poly1305
        """
        try:
            b64 = json.loads(json_input)
            jk = [ 'nonce', 'header', 'ciphertext', 'tag' ]
            jv = {k:base64.b64decode(b64[k]) for k in jk}
            
            key = self.sk[:32]
            cipher = ChaCha20_Poly1305.new(key=key, nonce=jv['nonce'])
            cipher.update(jv['header'])
            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])

            return plaintext
        except (ValueError, KeyError):
            print("Incorrect decryption")
        
        return b""

    def init_database(self):
        print("Creating database")
        try:
            conn = sqlite3.connect(self.dbfile)
            sqls = [
                "CREATE TABLE IF NOT EXISTS records(id TEXT, record BLOB)",
            ]

            for sql in sqls:
                conn.execute(sql)

            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def saveToDatabase(self, id, record):
        try:
            conn = sqlite3.connect(self.dbfile)
            sql = "INSERT INTO records VALUES (?, ?)"
            args = (id, record)
            conn.execute(sql, args)
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def getRecord(self, id):
        try:
            conn = sqlite3.connect(self.dbfile)
            sql = "SELECT record FROM records WHERE id = ?"
            args = (id, )
            rows = conn.execute(sql, args).fetchall()
            if rows.__len__ != 0:
                return rows
            else:
                return None
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()