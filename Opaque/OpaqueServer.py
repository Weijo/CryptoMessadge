import grpc
import opaque
import jwt
import datetime
import logging
from proto import opaque_pb2, opaque_pb2_grpc
from pysodium import randombytes, crypto_scalarmult_SCALARBYTES
from Util.RecordDB import RecordDB

logger = logging.getLogger(__name__)


class OpaqueAuthenticationServicer(opaque_pb2_grpc.OpaqueAuthenticationServicer):
    def __init__(self, db):
        # This key is only for generating jwt token
        self.server_key = randombytes(32)

        # Records
        self.record_key = randombytes(crypto_scalarmult_SCALARBYTES)
        self.db = db

        # For temporary caching of authentication tokens 
        self.auths = {}
        self.secs = {}

        self.context = "CryptoMessadge-opaque"

        self.server_id = "server"

    def RegisterUser(self, request, context):
        username = request.username
        message = request.message
        secS, resp = opaque.CreateRegistrationResponse(message, self.record_key)

        self.secs[username] = secS

        return opaque_pb2.RegistrationResponse(response=resp)

    def StoreRecord(self, request, context):
        username = request.username
        user_record = request.record
        
        # retrieve cached secS and remove from dictionary 
        ctx = self.secs.pop(username, None)
        
        if ctx == None:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid register phase")
            return opaque_pb2.FinalizeResponse(registered=False)

        if ( self.db.retrieve_record(username) != b""):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("User already exists")
            return opaque_pb2.FinalizeResponse(registered=False)

        rec = opaque.StoreUserRecord(ctx, user_record)

        self.db.store_record(username, rec)
        return opaque_pb2.FinalizeResponse(registered=True)

    def RequestCredentials(self, request, context):
        username = request.username
        user_request = request.request
        user_record = self.db.retrieve_record(username)
        if user_record == b"":
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return opaque_pb2.CredentialResponse()

        ids = opaque.Ids(username, self.server_id)
        resp, _, authU = opaque.CreateCredentialResponse(user_request, user_record, ids, self.context)

        self.auths[username] = authU

        return opaque_pb2.CredentialResponse(response=resp)

    def Authenticate(self, request, context):
        username = request.username
        auth = request.auth

        # Retrieve cached auth and remove from dictionary
        auth0 = self.auths.pop(username, None)
        

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
            payload = jwt.decode(encoded_token, self.server_key, algorithms="HS256")
        except Exception as e:
            logger.error(f"Verification error: {e}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token")
            return opaque_pb2.VerifyTokenResponse(is_valid=False)

        return opaque_pb2.VerifyTokenResponse(is_valid=True)