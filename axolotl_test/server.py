from concurrent import futures
import logging
import grpc
from proto import signalc_pb2
from proto import signalc_pb2_grpc
from queue import Queue
import json
import base64
from os.path import exists

CLIENT_STORE_FILEPATH = "client_store.json"


class ClientKey:
    def __init__(self, client_id, registration_id, device_id, identity_key_public, prekey_id, prekey, signed_prekey_id,
                 signed_prekey, signed_prekey_signature):
        self.client_id = client_id
        self.registration_id = registration_id
        self.device_id = device_id
        self.identity_key_public = identity_key_public
        self.prekey_id = prekey_id
        self.prekey = prekey
        self.signed_prekey_id = signed_prekey_id
        self.signed_prekey = signed_prekey
        self.signed_prekey_signature = signed_prekey_signature

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "registration_id": self.registration_id,
            "device_id": self.device_id,
            "identity_key_public": base64.b64encode(self.identity_key_public).decode('utf-8'),
            "prekey_id": self.prekey_id,
            "prekey": base64.b64encode(self.prekey).decode('utf-8'),
            "signed_prekey_id": self.signed_prekey_id,
            "signed_prekey": base64.b64encode(self.signed_prekey).decode('utf-8'),
            "signed_prekey_signature": base64.b64encode(self.signed_prekey_signature).decode('utf-8')
        }


class SignalKeyDistribution(signalc_pb2_grpc.SignalKeyDistributionServicer):
    def __init__(self):
        self.queues = {}

    def RegisterBundleKey(self, request, context):
        client_combine_key = ClientKey(request.clientId, request.registrationId, request.deviceId,
                                       request.identityKeyPublic, request.preKeyId, request.preKey,
                                       request.signedPreKeyId, request.signedPreKey, request.signedPreKeySignature)

        print('***** CLIENT REGISTER KEYS *****')
        print(request)

        self.SaveClientStore(client_combine_key)

        return signalc_pb2.BaseResponse(message='success')

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

    def GetKeyBundleByUserId(self, request, context):
        client_id = request.clientId
        print(client_id)
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

    def Publish(self, request, context):
        self.queues[request.receiveId].put(request)
        return signalc_pb2.BaseResponse(message='success')

    def Listen(self, request, context):
        print(self.queues)
        if request.clientId in self.queues:
            while True:
                publication = self.queues[request.clientId].get()  # blocking until the next .put for this queue
                publication_response = signalc_pb2.Publication(message=publication.message,
                                                               senderId=publication.senderId)
                yield publication_response

    def Subscribe(self, request, context):
        self.queues[request.clientId] = Queue()
        return signalc_pb2.BaseResponse(message='success')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    signalc_pb2_grpc.add_SignalKeyDistributionServicer_to_server(SignalKeyDistribution(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    print('Server has started at port: 50051')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
