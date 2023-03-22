from axolotl.state.identitykeystore import IdentityKeyStore
from axolotl.identitykey import IdentityKey
from axolotl.identitykeypair import IdentityKeyPair
from axolotl.util.keyhelper import KeyHelper
from axolotl.ecc.djbec import *
import sys


class LiteIdentityKeyStore(IdentityKeyStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        dbConn.execute("CREATE TABLE IF NOT EXISTS identities (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "recipient_id TEXT UNIQUE, device_id INTEGER,"
                       "registration_id INTEGER, public_key BLOB"
                       "next_prekey_id INTEGER, timestamp INTEGER);")
        
    def storeLocalData(self, device_id, recipient_id, registrationId, identityKeyPair):
        
        q = "INSERT OR IGNORE INTO identities(device_id, recipient_id, registration_id, public_key) VALUES(?, ?, ?, ?)"
        c = self.dbConn.cursor()
        pubKey = IdentityKey(DjbECPublicKey(identityKeyPair[1:])).serialize()

        if sys.version_info < (2,7):
            pubKey = buffer(pubKey)

        c.execute(q, (device_id,
                      recipient_id,
                      registrationId,
                      pubKey,
                      ))

        self.dbConn.commit()
