from axolotl.state.axolotlstore import AxolotlStore
from .liteidentitykeystore import LiteIdentityKeyStore
from .liteprekeystore import LitePreKeyStore
from .litesessionstore import LiteSessionStore
from .litesignedprekeystore import LiteSignedPreKeyStore
from .litesenderkeystore import LiteSenderKeyStore
import sqlite3


class LiteAxolotlStore(AxolotlStore):
    def __init__(self, db):
        conn = sqlite3.connect(db, check_same_thread=False)
        conn.text_factory = bytes
        self._db = db
        self.identityKeyStore = LiteIdentityKeyStore(conn)
        self.preKeyStore = LitePreKeyStore(conn)
        self.signedPreKeyStore = LiteSignedPreKeyStore(conn)
        self.sessionStore = LiteSessionStore(conn)
        self.senderKeyStore = LiteSenderKeyStore(conn)

    def __str__(self):
        return self._db
    
    def storeClientIdentityKey(self, device_id, recipient_id, registrationId, identityKeyPair):
        self.identityKeyStore.storeLocalData(device_id, recipient_id, registrationId, identityKeyPair)

    def storeClientPreKey(self, registrationId, prekey_id, prekey_publicKey):
        self.preKeyStore.storePreKey(registrationId, prekey_id, prekey_publicKey)

    def storeClientPreKeys(self, registrationId, prekeys):
        for prekey in prekeys:
            self.storeClientPreKey(registrationId, prekey.id, prekey.publicKey)

    def storeClientSignedPreKey(self, registration_id, signedPreKeyId, signedPreKeyRecord, signed_prekey_signature):
        self.signedPreKeyStore.storeSignedPreKey(registration_id, signedPreKeyId, signedPreKeyRecord, signed_prekey_signature)


    
    def getClientRegistrationId(self, recipient_id):
        return self.identityKeyStore.getRegistrationId(recipient_id)
    
    def getClientDeviceId(self, recipient_id):
        return self.identityKeyStore.getDeviceId(recipient_id)

    def getClientIdentityKey(self, recipient_id):
        return self.identityKeyStore.getIdentityKey(recipient_id)
    
    def getClientPreKey(self, registration_id):
        return self.preKeyStore.getPreKey(registration_id)
    
    def getClientSignedPreKey(self, registration_id):
        return self.signedPreKeyStore.getSignedPreKey(registration_id)
    
    def removeClientPreKey(self, registration_id, preKeyId):
        self.preKeyStore.removePreKey(registration_id, preKeyId)