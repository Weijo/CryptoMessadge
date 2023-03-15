import base64
import json
import threading
import grpc
import logging
from os.path import exists
from axolotl.invalidmessageexception import InvalidMessageException
from axolotl.untrustedidentityexception import UntrustedIdentityException
from proto import signalc_pb2
from proto import signalc_pb2_grpc
from axolotl.sessionbuilder import SessionBuilder
from axolotl.util.keyhelper import KeyHelper
from axolotl.identitykey import IdentityKey
from axolotl.ecc.djbec import DjbECPublicKey, DjbECPrivateKey
from axolotl.state.prekeyrecord import PreKeyRecord
from axolotl.state.signedprekeyrecord import SignedPreKeyRecord
from axolotl.protocol.prekeywhispermessage import PreKeyWhisperMessage
from axolotl.state.prekeybundle import PreKeyBundle
from axolotl.sessioncipher import SessionCipher
from .Store.mystore import MyStore

logger = logging.getLogger(__name__)

class SignalClient:
    def __init__(self, client_id, device_id, host, port, certfile, token):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.device_id = device_id
        self.token = token
        if exists(certfile):
            with open(certfile, 'rb') as f:
                creds = grpc.ssl_channel_credentials(f.read())
            self.channel = grpc.secure_channel(f"{self.host}:{self.port}", creds)
        else:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")

        self.stub = signalc_pb2_grpc.SignalKeyDistributionStub(self.channel)
        self.my_store = MyStore(self.client_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.channel:
            self.channel.close()
    
    def close(self):
        if self.channel:
            self.channel.close()
    
    def subscribe(self):
        request = signalc_pb2.SubscribeAndListenRequest(clientId=self.client_id)
        response = self.stub.Subscribe(request, metadata=[('token', self.token)])
        self.listen()

    def register_keys(self, device_id, signed_prekey_id):
        # generate client pre key and store it
        client_prekeys_pair = KeyHelper.generatePreKeys(1, 2)
        client_prekey_pair = client_prekeys_pair[0]
        
        self.my_store.storePreKey(client_prekey_pair.getId(), client_prekey_pair)

        client_signed_prekey_pair = KeyHelper.generateSignedPreKey(self.my_store.getIdentityKeyPair(), signed_prekey_id)
        client_signed_prekey_signature = client_signed_prekey_pair.getSignature()

        self.my_store.storeSignedPreKey(signed_prekey_id, client_signed_prekey_pair)

        request = signalc_pb2.SignalRegisterKeysRequest(
            clientId=self.client_id,
            registrationId=self.my_store.getLocalRegistrationId(),
            deviceId=device_id,
            identityKeyPublic=self.my_store.getIdentityKeyPair().getPublicKey().serialize(),
            preKeyId=client_prekey_pair.getId(),
            preKey=client_prekey_pair.serialize(),
            signedPreKeyId=signed_prekey_id,
            signedPreKey=client_signed_prekey_pair.serialize(),
            signedPreKeySignature=client_signed_prekey_signature,
        )

        response = self.stub.RegisterBundleKey(request, metadata=[('token', self.token)])

        if response.message == 'success':
            clientkey = {
                        "client_id":self.client_id,
                        "registration_id":self.my_store.getLocalRegistrationId(),
                        "device_id":device_id,
                        "identity_key_private":base64.b64encode(self.my_store.getIdentityKeyPair().getPrivateKey().serialize()).decode('utf-8'),
                        "identity_key_public":base64.b64encode(self.my_store.getIdentityKeyPair().getPublicKey().serialize()).decode('utf-8'),
                        }             
            self.SaveClientStore(clientkey)

    def SaveClientStore(self, clientkey):
        with open(self.client_id + ".json", 'w') as f:
                json.dump(clientkey, f, ensure_ascii=False)

    def listen(self):
        threading.Thread(target=self.heard, daemon=True).start()

    def heard(self):
        request = signalc_pb2.SubscribeAndListenRequest(clientId=self.client_id)
        for publication in self.stub.Listen(request, metadata=[('token', self.token)]):  # this line will wait for new messages from the server
            message_plain_text = self.decrypt_message(publication.message, publication.senderId)
            print("\nFrom {}: {}".format(publication.senderId, message_plain_text.decode('utf-8')))

            self.save_messages_to_local(publication.senderId, self.client_id, message_plain_text.decode('utf-8'))

    def save_messages_to_local(self, senderId, recipientId, message_plain_text):
        import datetime
        current_time = datetime.datetime.now()

        convo_id = self.get_other_user_id(senderId, recipientId)

        message = {
                    "senderId": senderId,
                    "recipientId": recipientId, 
                    "date":current_time.strftime("%x"), 
                    "time": current_time.strftime("%X"),
                    "message":message_plain_text
                }

        FILE_PATH = self.client_id + "_messages.json"
        file_exists = exists(FILE_PATH)
        if file_exists:
            with open(FILE_PATH) as json_file:
                messages = json.load(json_file)
            
            if convo_id not in messages:
                messages[convo_id] = {}
        else:
            messages = {convo_id: {}}
        
        messages[convo_id][current_time.strftime("%x %X")] = message
        
        with open(FILE_PATH, 'w') as f:
            json.dump(messages, f, ensure_ascii=False)

    def get_other_user_id(self, senderId, recipientId):
        if senderId != self.client_id:
            convo_id = senderId
        else:
            convo_id = recipientId
        return convo_id

    def publish(self, message, receiver_id):
        try:
            # encrypt message first
            out_goging_message = self.encrypt_message(message, receiver_id)
        except UntrustedIdentityException:
            print("publish - Unable to encrypt message to be sent, because a new session started on the recipient side.")

        else:
            # send message
            request = signalc_pb2.PublishRequest(receiveId=receiver_id, message=out_goging_message,
                                                 senderId=self.client_id)
            response = self.stub.Publish(request, metadata=[('token', self.token)])


    def GetReceiverKey(self, receiver_id):
        # get sender client key first (need to store in second time)
        request_receiver_key = signalc_pb2.SignalKeysUserRequest(clientId=receiver_id)

        response_receiver_key = self.stub.GetKeyBundleByUserId(request_receiver_key, metadata=[('token', self.token)])

        if response_receiver_key.clientId == 'none':
            return None

        return response_receiver_key
    
    def encrypt_message(self, message, receiver_id):
        self.save_messages_to_local(self.client_id, receiver_id, message)

        response_receiver_key = self.GetReceiverKey(receiver_id)

        # build session
        my_session_builder = SessionBuilder(self.my_store, self.my_store, self.my_store, self.my_store, receiver_id, 1)

        # combine key for receiver
        # identity public key
        receiver_identity_key_public = IdentityKey(DjbECPublicKey(response_receiver_key.identityKeyPublic[1:]))


        # pre key
        receiver_prekey = PreKeyRecord(serialized=response_receiver_key.preKey)

        # signed prekey
        receiver_signed_prekey_pair = SignedPreKeyRecord(serialized=response_receiver_key.signedPreKey)

        # combine prekey bundle
        receiver_prekey_bundle = PreKeyBundle(response_receiver_key.registrationId,
                                              response_receiver_key.deviceId,
                                              response_receiver_key.preKeyId,
                                              receiver_prekey.getKeyPair().getPublicKey(),
                                              response_receiver_key.signedPreKeyId,
                                              receiver_signed_prekey_pair.getKeyPair().getPublicKey(),
                                              response_receiver_key.signedPreKeySignature,
                                              receiver_identity_key_public)
        
        # process session and create session cipher
        my_session_builder.processPreKeyBundle(receiver_prekey_bundle)
        my_session_cipher = SessionCipher(self.my_store, self.my_store, self.my_store, self.my_store, receiver_id, 1)

        # encrypt message
        outgoing_message = my_session_cipher.encrypt(bytes(message, 'utf-8'))
        outgoging_message_serialize = outgoing_message.serialize()
        # print("Encrypt Message - Out Going Message =", outgoging_message_serialize)
        # return encrypt message
        return outgoging_message_serialize
    
    def decrypt_message(self, message, sender_id):
        # print("Decrypt Message - In Coming Message Encrypted=", message)
        incoming_message = PreKeyWhisperMessage(serialized=message)
        # init session to decrypt
        my_session_cipher = SessionCipher(self.my_store, self.my_store, self.my_store, self.my_store, sender_id, 1)
        try:
            message_plain_text = my_session_cipher.decryptPkmsg(incoming_message)
        except UntrustedIdentityException:
            print("Decrypt Message - Unable to decrypt, because a new session started on the sender side.")
        except InvalidMessageException:
            print("Decrypt Message - Unable to decrypt, because sender and recipient are the same.")
        else:
            # print("Decrypt Message - Plain Text Message =", message_plain_text)
            return message_plain_text
        # return encrypt message
        return 

    def close(self):
        self.channel.close()