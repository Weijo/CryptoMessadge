import grpc
from concurrent import futures
from proto import opaque_pb2, opaque_pb2_grpc
import opaque
import jwt
import datetime
import logging
from pysodium import crypto_secretbox, crypto_secretbox_open, randombytes

class OpaqueAuthenticationServicer(opaque_pb2_grpc.OpaqueAuthenticationServicer):
    def __init__(self):
        # Session keys for token verification
        self.session_keys = {}

        # TODO: Create user database to permanantly store 
        self.users = {}

        # This key is only for sealing ctx and jwt token
        self.server_key = randombytes(32)

        # Record key
        # TODO: Figure out a way to store keys securely
        self.record_key = ""

        self.context = "CryptoMessadge-opaque"

        self.server_id = "server"

    def RegisterUser(self, request, context):
        username = request.username
        message = request.message
        sec, resp = opaque.CreateRegistrationResponse(message)
        return opaque_pb2.RegistrationResponse(response=resp, context=self.seal(sec))

    def StoreRecord(self, request, context):
        username = request.username
        user_record = request.record
        ctx = self.unseal(request.context)
        if username in self.users:
            return opaque_pb2.FinalizeResponse(registered=False)

        rec = opaque.StoreUserRecord(ctx, user_record)
        self.users[username] = rec # TODO: Change this to permanent database

        return opaque_pb2.FinalizeResponse(registered=True)

    def RequestCredentials(self, request, context):
        username = request.username
        user_request = request.request

        user_record = self.users.get(username, "")
        if user_record == "":
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("User already exists")
            return opaque.CreateCredentialResponse()

        ids = opaque.Ids(username, self.server_id)
        resp, _, authU = opaque.CreateCredentialResponse(user_request, user_record, ids, self.context)
        
        return opaque_pb2.CredentialResponse(response=resp, context=self.seal(authU))

    def Authenticate(self, request, context):
        username = request.username
        auth = request.auth
        auth0 = self.unseal(request.context)

        try:
            opaque.UserAuth(auth, auth0)
        except:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid auth")
            return opaque_pb2.AuthenticationResponse()
        
        payload = {
            "id": username, 
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
        }

        token = jwt.encode(payload, self.server_key, algorithm="HS256")

        return opaque_pb2.AuthenticationResponse(token=token)


    def VerifyToken(self, request, context):
        encoded_token = request.token

        try:
            payload = jwt.decode(encoded_token, self.secret_key, algorithm="HS256")
        except Exception as e:
            logging.error(f"Verifcation error: {e}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token")
            return opaque_pb2.VerifyTokenResponse(is_valid=False)

        return opaque_pb2.VerifyTokenResponse(is_valid=True)

    
    def seal(self, data):
        nonce = randombytes(24)
        return nonce+crypto_secretbox(data, nonce, self.server_key)

    def unseal(self, data):
        nonce = data[:24]
        return crypto_secretbox_open(data[24:], nonce, self.server_key)

def serve():
    logging.info("Starting server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    opaque_pb2_grpc.add_OpaqueAuthenticationServicer_to_server(
        OpaqueAuthenticationServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve()
