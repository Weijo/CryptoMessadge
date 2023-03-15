import grpc
from proto import opaque_pb2, opaque_pb2_grpc
import opaque
import logging

class OpaqueClient:
    def __init__(self, host: str, port: str):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = opaque_pb2_grpc.OpaqueAuthenticationStub(self.channel)
        self.context = "CryptoMessadge-opaque"
        self.server_id = "server"

    def register_user(self, username: str, password: str) -> bool:
        """Registers with the server
        @param: username
        @param: password
        @return: registered - whether you have successfully registered or not
        """
        # Generate Registration Request
        security_context, message = opaque.CreateRegistrationRequest(password)
        request = opaque_pb2.RegistrationRequest(username=username, message=message)

        # Send Registration Request to the server
        response = self.stub.RegisterUser(request)

        # Retrieve the RegistrationResponse from the server
        resp = response.response
        ids = opaque.Ids(username, self.server_id)
        
        # Generate user record, export key is not needed
        user_record, _ = opaque.FinalizeRequest(security_context, resp, ids)

        # Build the finalize request
        finalize_request = opaque_pb2.FinalizeRequest(username=username, record=user_record, context=response.context)
        # Send the request to the server
        response = self.stub.StoreRecord(finalize_request)

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
        pub, security_context = opaque.CreateCredentialRequest(password)
        request = opaque_pb2.CredentialRequest(username=username, request=pub)

        # Send Credential Request to the server
        response = self.stub.RequestCredentials(request)

        # Retrieve the Credential Response from the server
        resp = response.response
        ctx = response.context

        # Recover Credentials
        # Shared key and export key not needed
        try:
            _, authU, _ = opaque.RecoverCredentials(resp, security_context, self.context, ids)
        except ValueError:
            logging.error("Invalid password")
            return ""

        # Generate Authentication request
        auth_request = opaque_pb2.AuthenticationRequest(username=username, auth=authU, context=response.context)
        # Send Authentication request to the server
        response = self.stub.Authenticate(auth_request)
        # Retrieve Authentication response from the server
        token = response.token
        return token
