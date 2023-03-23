import base64
import json
import logging
import threading

import grpc
from os.path import exists
from datetime import datetime
from axolotl.ecc.djbec import DjbECPrivateKey, DjbECPublicKey
from axolotl.identitykey import IdentityKey
from axolotl.invalidmessageexception import InvalidMessageException
from axolotl.protocol.prekeywhispermessage import PreKeyWhisperMessage
from axolotl.sessionbuilder import SessionBuilder
from axolotl.sessioncipher import SessionCipher
from axolotl.state.prekeybundle import PreKeyBundle
from axolotl.state.prekeyrecord import PreKeyRecord
from axolotl.state.signedprekeyrecord import SignedPreKeyRecord
from axolotl.untrustedidentityexception import UntrustedIdentityException
from axolotl.util.keyhelper import KeyHelper
from Util.ClientStore.sqlite.liteaxolotstore import LiteAxolotlStore
from Signal.AxolotlManager import AxolotlManager

import Util.messageStorage
from proto import signalc_pb2, signalc_pb2_grpc

logger = logging.getLogger(__name__)


class SignalClient:
    def __init__(self, client_id, device_id, host, port, certfile, token, dbpath):
        self.host = host
        self.port = port
        self.msg_id = 1
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
        self.my_store = LiteAxolotlStore(dbpath)
        self.manager = AxolotlManager(self.my_store, self.client_id)

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
        self.manager.level_prekeys()
        signedprekey  = self.manager.load_latest_signed_prekey(generate=True)

        prekeys = []
        my_list = []
        for prekey_detail in self.my_store.loadUnsentPendingPreKeys():
            prekey = signalc_pb2.PreKeyRecord(
                id=prekey_detail.getId(),
                publicKey=prekey_detail.getKeyPair().getPublicKey().serialize(),
            )
            prekeys.append(prekey)
            my_list.append(prekey_detail.getId())

        request = signalc_pb2.SignalRegisterKeysRequest(
            clientId=self.client_id,
            registrationId=self.my_store.getLocalRegistrationId(),
            deviceId=device_id,
            identityKeyPublic=self.my_store.getIdentityKeyPair().getPublicKey().serialize(),
            preKeys=prekeys,
            signedPreKeyId=signedprekey.getId(),
            signedPreKey=signedprekey.getKeyPair().getPublicKey().serialize(),
            signedPreKeySignature=signedprekey.getSignature(),
        )

        response = self.stub.RegisterBundleKey(request, metadata=[('token', self.token)])

        if response.message == 'success':
            self.my_store.setPrekeyAsSent(my_list)   # hardcoded, to change

    def SaveClientStore(self, clientkey):
        with open(self.client_id + ".json", 'w') as f:
            json.dump(clientkey, f, ensure_ascii=False)

    def listen(self):
        threading.Thread(target=self.heard, daemon=True).start()

    def heard(self):
        request = signalc_pb2.SubscribeAndListenRequest(clientId=self.client_id)
        for publication in self.stub.Listen(request, metadata=[('token', self.token)]):  # this line will wait for new messages from the server
            message_plain_text = self.decrypt_message(publication.message, publication.senderId)

            try:
                print("\nFrom {}: {}".format(publication.senderId, message_plain_text.decode('utf-8')))
            except AttributeError as e:
                print(e)

            self.save_messages_to_local(publication.senderId, self.client_id, message_plain_text.decode('utf-8'))

            yield message_plain_text.decode('utf-8')

    def save_messages_to_local(self, senderId, recipientId, message_plain_text):

        current_datetime = datetime.now()
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

        # convo_id = self.get_other_user_id(senderId, recipientId)
        convo_id = senderId + "-" + recipientId

        # Define password and salt
        password = b"1ct2205?!"
        salt = b"verysaltytears"

        # Derive the encryption key and create an instance of the Fernet class
        key = Util.messageStorage.get_encryption_key(password, salt)
        cipher_suite = Util.messageStorage.create_cipher_suite(key)

        encrypted_message_for_storage = Util.messageStorage.encrypt_body(cipher_suite, message_plain_text).decode(
            'utf-8')

        # connect to database.
        conn = Util.messageStorage.connect_to_database()

        # If already got entry in database, get the latest messageId, and increase that number by 1.
        if not Util.messageStorage.database_empty(conn):
            self.msg_id = Util.messageStorage.get_latest_message_id(conn) + 1

        # Insert data into the table
        messages = [
            (self.msg_id, convo_id, senderId, recipientId, encrypted_message_for_storage, current_datetime),
        ]

        Util.messageStorage.insert_messages(conn, messages)

        # Retrieve the data from the table and print it in a table format
        Util.messageStorage.print_messages(conn)

        # Close the database connection
        Util.messageStorage.close_database(conn)

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

    def GetReceiverKey(self, receiver_id, isEncrypting):
        # get sender client key first (need to store in second time)
        request_receiver_key = signalc_pb2.SignalKeysUserRequest(clientId=receiver_id, isEncrypting=isEncrypting)

        response_receiver_key = self.stub.GetKeyBundleByUserId(request_receiver_key, metadata=[('token', self.token)])

        if response_receiver_key.clientId == 'none':
            return None
        return response_receiver_key

    def encrypt_message(self, message, receiver_id):

        response_receiver_key = self.GetReceiverKey(receiver_id, True)

        # build session
        my_session_builder = SessionBuilder(self.my_store, self.my_store, self.my_store, self.my_store, receiver_id, 1)

        # combine key for receiver
        # identity public key
        receiver_identity_key_public = IdentityKey(DjbECPublicKey(response_receiver_key.identityKeyPublic[1:]))

        # pre key
        # receiver_prekey = PreKeyRecord(serialized=response_receiver_key.preKey)
        receiver_prekey = DjbECPublicKey(response_receiver_key.preKey.publicKey[1:])

        # signed prekey
        # receiver_signed_prekey_pair = SignedPreKeyRecord(serialized=response_receiver_key.signedPreKey)
        receiver_signed_prekey_pair = DjbECPublicKey(response_receiver_key.signedPreKey[1:])

        # combine prekey bundle
        receiver_prekey_bundle = PreKeyBundle(response_receiver_key.registrationId,
                                              response_receiver_key.deviceId,
                                              response_receiver_key.preKey.id,
                                              receiver_prekey,
                                              response_receiver_key.signedPreKeyId,
                                              receiver_signed_prekey_pair,
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
