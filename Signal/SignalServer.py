import logging
import json
import base64
import grpc
from proto import signalc_pb2
from proto import signalc_pb2_grpc
from proto import opaque_pb2
from proto import opaque_pb2_grpc
from queue import Queue
from Util.ServerStore.sqlite.liteaxolotstore import LiteAxolotlStore
from os.path import exists

logger = logging.getLogger(__name__)

CLIENT_STORE_FILEPATH = "client_store.json"
OPAQUE_HOST = 'localhost:50051'
CERTIFILE_FILE = './localhost.crt'

def require_auth(func):
    def wrapper(self, request, context):
        # Get token from context metadata
        metadata = dict(context.invocation_metadata())
        token = metadata.get('token', '')
        if token == "":
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid token')

        # Call VerifyToken method on OpaqueAuthenticationServicer
        if exists(CERTIFILE_FILE):
            with open(CERTIFILE_FILE, 'rb') as f:
                creds = grpc.ssl_channel_credentials(f.read())
            channel = grpc.secure_channel(OPAQUE_HOST, creds)
        else:
            channel = grpc.insecure_channel(OPAQUE_HOST)

        stub = opaque_pb2_grpc.OpaqueAuthenticationStub(channel)
        response = stub.VerifyToken(opaque_pb2.VerifyTokenRequest(token=token))

        # Check if token is valid
        if not response.is_valid:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid token')
        else:
            return func(self, request, context)

    return wrapper

class ClientKey:
    def __init__(self, client_id, registration_id, device_id, identity_key_public, prekeys, signed_prekey_id,
                 signed_prekey, signed_prekey_signature):
        self.client_id = client_id
        self.registration_id = registration_id
        self.device_id = device_id
        self.identity_key_public = identity_key_public
        self.prekeys = prekeys
        self.signed_prekey_id = signed_prekey_id
        self.signed_prekey = signed_prekey
        self.signed_prekey_signature = signed_prekey_signature

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "registration_id": self.registration_id,
            "device_id": self.device_id,
            "identity_key_public": base64.b64encode(self.identity_key_public).decode('utf-8'),
            "signed_prekey_id": self.signed_prekey_id,
            "signed_prekey": base64.b64encode(self.signed_prekey).decode('utf-8'),
            "signed_prekey_signature": base64.b64encode(self.signed_prekey_signature).decode('utf-8')
        }


class SignalKeyDistribution(signalc_pb2_grpc.SignalKeyDistributionServicer):
    def __init__(self):
        self.queues = {}
        self.my_store = LiteAxolotlStore("ServerStore.db")

    def GetClientStore(self):
        data = {}
        file_exists = exists(CLIENT_STORE_FILEPATH)
        if file_exists:
            with open(CLIENT_STORE_FILEPATH) as json_file:
                data = json.load(json_file)
        return data

    def SaveClientStore(self, client_combine_key):
        data = self.GetClientStore()

        data[client_combine_key.client_id] = client_combine_key.to_dict()

        with open(CLIENT_STORE_FILEPATH, 'w') as f:
            json.dump(data, f, ensure_ascii=False)

    @require_auth
    def RegisterBundleKey(self, request, context):
        client_combine_key = ClientKey(request.clientId, request.registrationId, request.deviceId,
                                       request.identityKeyPublic, request.preKeys,
                                       request.signedPreKeyId, request.signedPreKey, request.signedPreKeySignature)

        logger.debug('***** CLIENT REGISTER KEYS *****')
        logger.debug(request)

        self.SaveClientStore(client_combine_key)

        self.my_store.storeClientIdentityKey(client_combine_key.device_id, client_combine_key.client_id, client_combine_key.registration_id, client_combine_key.identity_key_public)
        self.my_store.storeClientPreKeys(client_combine_key.registration_id, client_combine_key.prekeys)
        self.my_store.storeClientSignedPreKey(client_combine_key.registration_id, client_combine_key.signed_prekey_id, client_combine_key.signed_prekey)

        return signalc_pb2.BaseResponse(message='success')

    @require_auth
    def GetKeyBundleByUserId(self, request, context):
        client_id = request.clientId
        logger.debug(client_id)
        if client_id in self.GetClientStore():
            client_combine_key = self.GetClientStore()[client_id]
            response = signalc_pb2.SignalKeysUserResponse(
                clientId=client_id,
                registrationId=client_combine_key['registration_id'],
                deviceId=client_combine_key['device_id'],
                identityKeyPublic=base64.b64decode(client_combine_key['identity_key_public']),
                preKeyId=client_combine_key['prekey_id'],
                preKey=base64.b64decode(client_combine_key['prekey']),
                signedPreKeyId=client_combine_key['signed_prekey_id'],
                signedPreKey=base64.b64decode(client_combine_key['signed_prekey']),
                signedPreKeySignature=base64.b64decode(client_combine_key['signed_prekey_signature'])
            )
        else:
            response = signalc_pb2.SignalKeysUserResponse(
                clientId='none',
                registrationId=0,
                deviceId=0,
                identityKeyPublic=str.encode("none"),
                preKeyId=0,
                preKey=str.encode("none"),
                signedPreKeyId=0,
                signedPreKey=str.encode("none"),
                signedPreKeySignature=str.encode("none")
            )
        return response

    @require_auth
    def Publish(self, request, context):
        self.queues[request.receiveId].put(request)
        return signalc_pb2.BaseResponse(message='success')

    @require_auth
    def Listen(self, request, context):
        logger.debug(self.queues)
        if request.clientId in self.queues:
            while True:
                publication = self.queues[request.clientId].get()  # blocking until the next .put for this queue
                publication_response = signalc_pb2.Publication(message=publication.message,
                                                               senderId=publication.senderId)
                yield publication_response

    @require_auth
    def Subscribe(self, request, context):
        self.queues[request.clientId] = Queue()
        return signalc_pb2.BaseResponse(message='success')