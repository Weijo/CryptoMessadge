from axolotl.state.signedprekeystore import SignedPreKeyStore
from axolotl.state.signedprekeyrecord import SignedPreKeyRecord
from axolotl.invalidkeyidexception import InvalidKeyIdException
from axolotl.ecc.djbec import *
import sys

class LiteSignedPreKeyStore(SignedPreKeyStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        dbConn.execute("CREATE TABLE IF NOT EXISTS signed_prekeys (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "registration_id INTEGER, prekey_id INTEGER, timestamp INTEGER, record BLOB, signature BLOB, UNIQUE(registration_id, prekey_id) ON CONFLICT IGNORE);")

    def storeSignedPreKey(self, registration_id, signedPreKeyId, signedPreKeyRecord, signed_prekey_signature):
        q = "INSERT OR IGNORE INTO signed_prekeys (registration_id, prekey_id, record, signature) VALUES(?,?,?,?)"
        cursor = self.dbConn.cursor()

        record = DjbECPublicKey(signedPreKeyRecord[1:]).serialize()

        cursor.execute(q, (registration_id, signedPreKeyId, record, signed_prekey_signature))
        self.dbConn.commit()

    def getSignedPreKey(self, registration_id):
        q = "SELECT prekey_id, record, signature from signed_prekeys WHERE registration_id = ? ORDER BY prekey_id DESC"

        cursor = self.dbConn.cursor()
        cursor.execute(q, (registration_id,))

        result = cursor.fetchone()

        return result if result else None