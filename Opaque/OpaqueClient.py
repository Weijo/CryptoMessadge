import grpc
import opaque
import logging
from os.path import exists
from proto import opaque_pb2, opaque_pb2_grpc

logger = logging.getLogger(__name__)


class OpaqueClient:
    def __init__(self, host: str, port: int, certfile: str):
        self.host = host
        self.port = port
        if exists(certfile):
            with open(certfile, 'rb') as f:
                creds = grpc.ssl_channel_credentials(f.read())
            self.channel = grpc.secure_channel(f"{self.host}:{self.port}", creds)
        else:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = opaque_pb2_grpc.OpaqueAuthenticationStub(self.channel)
        self.context = "CryptoMessadge-opaque"
        self.server_id = "server"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.channel:
            self.channel.close()
    
    def close(self):
        if self.channel:
            self.channel.close()

    def register_user(self, username: str, password: str) -> bool:
        """Registers with the server
        @param: username
        @param: password
        @return: registered - whether you have successfully registered or not
        """
        # Generate Registration Request
        secU, M = opaque.CreateRegistrationRequest(password.encode())
        request = opaque_pb2.RegistrationRequest(username=username, message=M)

        # Send Registration Request to the server
        response = self.stub.RegisterUser(request)

        # Retrieve the RegistrationResponse from the server
        pub = response.response
        ids = opaque.Ids(username, self.server_id)
        
        # Generate user record, export key is not needed
        user_record, export_key = opaque.FinalizeRequest(secU, pub, ids)

        # Build the finalize request
        finalize_request = opaque_pb2.FinalizeRequest(username=username, record=user_record, context=response.context)
        # Send the request to the server
        try:
            response = self.stub.StoreRecord(finalize_request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                logger.error(f"User: {username} already exists")
                return False
            else:
                logger.error("Unexpected error: {}".format(e))
                return False

        # Retrieve the response from the server
        registered = response.registered
        return registered
    
    def login(self, username: str, password: str) -> str:
        """Logs in with the server
        @param: username
        @param: password
        @return: token - jwt token for authentication
        """
        # Generate Credential Request
        ids = opaque.Ids(username, self.server_id)
        pub, security_context = opaque.CreateCredentialRequest(password.encode())
        request = opaque_pb2.CredentialRequest(username=username, request=pub)

        # Send Credential Request to the server
        try:
            response = self.stub.RequestCredentials(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.error(f"User: {username} does not exist")
                return ""
            else:
                logger.error("Unexpected error: {}".format(e))
                return ""

        # Retrieve the Credential Response from the server
        resp = response.response
        ctx = response.context

        # Recover Credentials
        # Shared key and export key not needed
        try:
            sk, authU, export_key = opaque.RecoverCredentials(resp, security_context, self.context, ids)
        except ValueError:
            logger.error("Invalid username or password")
            return ""

        # Generate Authentication request
        auth_request = opaque_pb2.AuthenticationRequest(username=username, auth=authU, context=ctx)
    
        # Send Authentication request to the server
        try:
            response = self.stub.Authenticate(auth_request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                logger.error(f"Invalid auth: {e.details()}")
                return ""
            else:
                logger.error("Unexpected error: {}".format(e))
                return ""
        # Retrieve Authentication response from the server
        token = response.token
        return token
    