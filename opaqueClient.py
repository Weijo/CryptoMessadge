import opaque
import socket
import base64
import json
from Crypto.Cipher import ChaCha20_Poly1305


class opaqueClient:
    def __init__(self, server) -> None:
        self.server = server
        self.context = "CryptoMessadge"

    def register(self, username: str, password: str) -> None:
        """
        Registers with the server using the OPAQUE protocol
        """
        ids = opaque.Ids(username, "server")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server)

            # Step 1: User creates a registration request
            security_context, message = opaque.CreateRegistrationRequest(password)

            # Send type 1 request to server 
            dictionary = {"id": username, "message": base64.b64encode(message).decode('utf-8')}
            request = json.dumps(dictionary).encode()
            request_type_bytes = bytes([1])
            request = request_type_bytes + request

            print(f"{request=}")
            sock.sendall(request)

            # Receive Step 2:
            server_pub_b64 = sock.recv(1024).strip()
            print(f"{server_pub_b64=}")
            server_pub = base64.b64decode(server_pub_b64)

            # Step 3: The user finalizes the registration using the response from the server
            # export key is not needed
            user_record, _ = opaque.FinalizeRequest(security_context, server_pub, ids)

            user_record_b64 = base64.b64encode(user_record)

            print(f"{user_record_b64=}")
            sock.sendall(user_record_b64)

    def login(self, username: str, password: str) -> bytes:
        """
        Initiates an Authenticated key exchange using OPAQUE protocol
        """
        ids = opaque.Ids(username, "server")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)

        # Step 1: The user initiates a credential request
        pub, security_context = opaque.CreateCredentialRequest(password)

        # Send type 2 request to server 
        dictionary = {"id": username, "message": base64.b64encode(pub).decode('utf-8')}
        request = json.dumps(dictionary).encode()
        request_type_bytes = bytes([2])
        request = request_type_bytes + request

        print(f"{request=}")
        self.sock.sendall(request)

        # Receive Step 2:
        resp_b64 = self.sock.recv(1024).strip()
        print(f"{resp_b64=}")
        resp = base64.b64decode(resp_b64)

        # Step 3: The user recovers its credentials from the server's response
        # export_key not needed
        sk, authU, _ = opaque.RecoverCredentials(resp, security_context, self.context, ids)

        # Step 4: Server authenticates the user
        authU_b64 = base64.b64encode(authU)
        print(f"{authU_b64}")
        self.sock.sendall(authU_b64)

        # Receive authentication response
        authentication = self.sock.recv(1024).strip()
        print(authentication)

        if authentication == b"True":
            self.sk = sk
            self.username = username
        else:
            print("Invalid credential")
            self.sk = b""

    def sendMessage(self, message: bytes) -> bytes:
        if self.sk == b"":
            print("No authenticated session found")
            return

        data = self.encrypt(message)
        self.sock.sendall(data.encode())

        json_resp = self.sock.recv(1024).strip()
        resp = self.decrypt(json_resp)
        return resp

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt using ChaCha20_Poly1305
        """
        # OPAQUE's key is 64 bytes
        key = self.sk[:32]
        header = self.username.encode()
        cipher = ChaCha20_Poly1305.new(key=key)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        jk = ['nonce', 'header', 'ciphertext', 'tag']
        jv = [base64.b64encode(x).decode('utf-8') for x in (cipher.nonce, header, ciphertext, tag)]
        result = json.dumps(dict(zip(jk, jv)))
        return result

    def decrypt(self, json_input: bytes) -> bytes:
        """
        Decryption using ChaCha20_Poly1305
        """
        try:
            b64 = json.loads(json_input)
            jk = ['nonce', 'header', 'ciphertext', 'tag']
            jv = {k: base64.b64decode(b64[k]) for k in jk}

            key = self.sk[:32]
            cipher = ChaCha20_Poly1305.new(key=key, nonce=jv['nonce'])
            cipher.update(jv['header'])
            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])

            return plaintext
        except (ValueError, KeyError):
            print("Incorrect decryption")

        return b""

    def close(self):
        self.sock.close()

    def sendToServer(self, request: bytes, request_type: int) -> bytes:
        """
        type: 1 - register
        type: 2 - login (Authenticated Key Exchange)
        """

        request_type_bytes = bytes([request_type])
        request = request_type_bytes + request

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server)

            sock.sendall(request)

            received = sock.recv(1024)

        return received
